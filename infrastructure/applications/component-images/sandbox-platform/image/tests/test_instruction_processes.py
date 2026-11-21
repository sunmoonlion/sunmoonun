"""Worker route configuration and the only HTTP endpoint exposed to Codex."""

import http.client
import json
import sys
import threading
from http.server import HTTPServer
from pathlib import Path

import pytest
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import instruction_gateway as gateway
from instruction_worker import configure


def test_worker_model_name_is_data_and_ipv6_route_is_literal(tmp_path):
    model = 'test"\n[features]'
    configure(tmp_path, "::1", model)
    cfg = tomllib.loads((tmp_path / "config.toml").read_text())
    assert cfg["model"] == model
    assert cfg["model_providers"]["instruction"]["base_url"] == "http://[::1]:47801/v1"
    assert not cfg["agents"]["enabled"] and not cfg["features"]["shell_tool"]
    assert not tomllib.loads((tmp_path / "environments.toml").read_text())[
        "include_local"
    ]
    with pytest.raises(ValueError):
        configure(tmp_path, "arbitrary.example", model)


def test_gateway_only_accepts_json_and_uses_host_observed_turn(tmp_path, monkeypatch):
    monkeypatch.setattr(gateway, "BINDING", tmp_path)
    (tmp_path / "turn").write_text("observed")
    seen = []

    class Control:
        def relay(self, body, *, turn_id, start, write):
            seen.append((body, turn_id))
            start()
            write(b"data: model-event\n\n")

    with HTTPServer(("127.0.0.1", 0), gateway.Gateway) as server:
        server.control = Control()
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:

            def post(path, raw):
                conn = http.client.HTTPConnection(*server.server_address, timeout=2)
                try:
                    conn.request(
                        "POST", path, raw, headers={"X-Instruction-Turn": "untrusted"}
                    )
                    with conn.getresponse() as result:
                        return result.status, result.read()
                finally:
                    conn.close()

            assert post("/v1/responses", json.dumps({"model": "test"})) == (
                200,
                b"data: model-event\n\n",
            )
            assert post("/v1/responses", "[]")[0] == 403
            assert post("/other", "{}")[0] == 404
            assert seen == [({"model": "test"}, "observed")]
        finally:
            server.shutdown()
            thread.join()
