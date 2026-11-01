import importlib.util
import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "moonshot_responses", Path(__file__).parents[1] / "moonshot_responses.py"
)
compat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compat)


def empty():
    return {
        "type": "message",
        "role": "assistant",
        "content": [{"type": "output_text", "text": ""}],
    }


def failing_history():
    return {
        "model": "kimi-k3",
        "tools": [{"type": "web_search"}],
        "input": [
            {
                "type": "function_call",
                "name": "lookup",
                "namespace": "probe",
                "call_id": "probe--_--lookup_0_abc",
                "arguments": "{}",
            },
            {
                "type": "function_call",
                "name": "lookup",
                "namespace": "probe",
                "call_id": "probe--_--lookup_1_def",
                "arguments": "{}",
            },
            empty(),
            {
                "type": "function_call_output",
                "call_id": "probe--_--lookup_0_abc",
                "output": "A",
            },
            {
                "type": "function_call_output",
                "call_id": "probe--_--lookup_1_def",
                "output": "B",
            },
        ],
    }


def test_removes_only_empty_message_preserving_pairing_order_and_search():
    source = failing_history()
    normalized, count = compat.normalize_request(json.dumps(source).encode())
    result = json.loads(normalized)
    assert count == 1
    assert result == {**source, "input": source["input"][:2] + source["input"][3:]}
    assert compat.normalize_request(normalized) == (normalized, 0)


@pytest.mark.parametrize(
    "item",
    [
        {**empty(), "role": "user"},
        {**empty(), "content": [{"type": "output_text", "text": " "}]},
        {
            **empty(),
            "content": [
                {
                    "type": "output_text",
                    "text": "",
                    "annotations": [{"type": "url_citation"}],
                }
            ],
        },
        {**empty(), "content": [{"type": "refusal", "refusal": "No"}]},
        {**empty(), "content": [{"type": "image", "url": "example"}]},
        {**empty(), "tool_calls": [{"id": "call-1"}]},
        {"type": "reasoning", "content": []},
    ],
)
def test_content_and_non_assistant_items_are_not_discarded(item):
    body = json.dumps({"input": [item]}).encode()
    assert compat.normalize_request(body) == (body, 0)


@pytest.mark.parametrize(
    "body", [b"not json", b"[]", b'{"input":"hello"}', b'{ "input": [] }']
)
def test_unaffected_body_is_byte_for_byte_unchanged(body):
    assert compat.normalize_request(body) == (body, 0)


def test_provider_selection_is_explicitly_scoped():
    config = {
        "model_provider": "kimi",
        "model_providers": {"kimi": {"base_url": "https://api.moonshot.cn/v1"}},
    }
    assert compat.selected_provider(config) == ("kimi", "https://api.moonshot.cn/v1")
    assert compat.selected_provider({}) is None
    config["model_providers"]["kimi"]["base_url"] = "https://another-provider.test/v1"
    assert compat.selected_provider(config) is None


def test_http_transport_preserves_auth_sse_and_upstream_errors(capsys):
    received = []

    class Upstream(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            received.append((body, self.headers.get("Authorization")))
            failure = body.get("force_error", False)
            self.send_response(400 if failure else 200)
            self.send_header(
                "Content-Type", "application/json" if failure else "text/event-stream"
            )
            self.send_header("Msh-Request-Id", "diagnostic-request")
            self.end_headers()
            self.wfile.write(
                b'{"error":"original error"}'
                if failure
                else b'data: {"type":"response.completed"}\n\n'
            )

    upstream = ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
    relay = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        compat.handler_for(f"http://127.0.0.1:{upstream.server_port}/v1"),
    )
    for server in (upstream, relay):
        threading.Thread(target=server.serve_forever, daemon=True).start()
    try:

        def request(payload):
            return urllib.request.Request(
                f"http://127.0.0.1:{relay.server_port}/v1/responses",
                data=json.dumps(payload).encode(),
                headers={
                    "Authorization": "Bearer TEST-ONLY",
                    "Content-Type": "application/json",
                },
            )

        with urllib.request.urlopen(request(failing_history())) as response:
            assert response.read() == b'data: {"type":"response.completed"}\n\n'
            assert response.headers["Msh-Request-Id"] == "diagnostic-request"
        assert len(received[0][0]["input"]) == 4
        assert received[0][1] == "Bearer TEST-ONLY"
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request({"force_error": True}))
        assert error.value.code == 400
        assert error.value.read() == b'{"error":"original error"}'
    finally:
        for server in (relay, upstream):
            server.shutdown()
            server.server_close()
    captured = capsys.readouterr()
    assert "TEST-ONLY" not in captured.out + captured.err
    assert "removed_empty_assistant_messages=1" in captured.err
    assert captured.out == ""
