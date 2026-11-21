import http.client
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location(
    "instruction_responses", Path(__file__).parents[1] / "instruction_responses.py"
)
relay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(relay)
ENDPOINT = "https://model.example.test/v1/responses"


def exercise(
    events,
    *,
    status=200,
    disconnected=False,
    authorized=ENDPOINT,
    sent=None,
    receipts=None,
):
    sent = [] if sent is None else sent
    receipts = [] if receipts is None else receipts
    wire = b"".join(b"data: " + json.dumps(e).encode() + b"\r\n\r\n" for e in events)
    wire = (
        f"HTTP/1.1 {status} response\r\nContent-Type: text/event-stream\r\n\r\n".encode()
        + wire
    )

    def connect(host, port, *, timeout):
        assert authorized == ENDPOINT and (host, port) == ("model.example.test", 443)

        def getresponse():
            result = http.client.HTTPResponse(
                SimpleNamespace(makefile=lambda *args: io.BytesIO(wire))
            )
            result.begin()
            return result

        return SimpleNamespace(
            request=lambda *a, **kw: sent.append((a, kw)),
            getresponse=getresponse,
            close=lambda: None,
        )

    def write(_):
        if disconnected:
            raise BrokenPipeError()

    relay.forward(
        {"model": "m"},
        endpoint=ENDPOINT,
        credential_id="installed",
        api_key="fixture",
        claim=lambda body, key: (authorized, {**body, "max_output_tokens": 10}),
        receipt=lambda key, usage: receipts.append((key, usage)),
        start=lambda: None,
        write=write,
        connect=connect,
    )
    assert len(sent) == 1 and sent[0][0] == ("POST", "/v1/responses")
    assert json.loads(sent[0][1]["body"]) == {"model": "m", "max_output_tokens": 10}
    return receipts


def event(kind, **fields):
    return {"type": "response." + kind, "response": {"id": "r", **fields}}


@pytest.mark.parametrize("kind", ["completed", "incomplete", "failed"])
def test_final_usage_still_collected_after_reader_disconnects(kind):
    usage = {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3}
    assert exercise(
        [event("created"), event(kind, usage=usage)], disconnected=True
    ) == [("r", usage)]


def test_missing_meter_has_no_receipt():
    assert exercise([event("created"), event("failed")]) == []


def test_unrelated_completion_and_redirect_do_not_supply_usage():
    with pytest.raises(ValueError, match="identity"):
        exercise([event("created"), event("completed", id="other", usage={})])
    with pytest.raises(ValueError, match="no Responses event stream"):
        exercise([], status=307)


def test_route_mismatch_precedes_any_connection():
    with pytest.raises(ValueError, match="authorized route"):
        exercise([], authorized="https://other.example.test/v1/responses")


def test_provider_401_is_reported_without_retry_or_usage():
    sent, receipts = [], []
    with pytest.raises(relay.ProviderAuthenticationRejected):
        exercise([], status=401, sent=sent, receipts=receipts)
    assert len(sent) == 1 and receipts == []
