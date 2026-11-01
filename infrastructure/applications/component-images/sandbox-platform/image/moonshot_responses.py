"""Keep empty assistant messages out of Moonshot Responses history.

Moonshot can emit an empty message between function_call and its output, then
reject its own history on the next request. Only that content-free item is
removed. Tool IDs, nonempty messages, native search and responses are unchanged.
This is a loopback transport owned by the user's sandbox, not an agent runner.
"""

from __future__ import annotations

import http.server
import json
import os
import re
import signal
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import tomllib

HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def is_empty_assistant(item: object) -> bool:
    if not isinstance(item, dict) or item.get("type") != "message":
        return False
    if item.get("role") != "assistant" or item.get("tool_calls") or item.get("refusal"):
        return False
    content = item.get("content")
    return isinstance(content, list) and all(
        isinstance(part, dict)
        and part.get("type") == "output_text"
        and part.get("text") == ""
        and not part.get("annotations")
        for part in content
    )


def normalize_request(body: bytes) -> tuple[bytes, int]:
    """Preserve bytes unless there are empty assistant items to remove."""
    try:
        request = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return body, 0
    if not isinstance(request, dict) or not isinstance(request.get("input"), list):
        return body, 0
    items = request["input"]
    retained = [item for item in items if not is_empty_assistant(item)]
    removed = len(items) - len(retained)
    if not removed:
        return body, 0
    request["input"] = retained
    return json.dumps(request, ensure_ascii=False).encode(), removed


def selected_provider(config: dict) -> tuple[str, str] | None:
    name = config.get("model_provider")
    provider = config.get("model_providers", {}).get(name, {})
    base = provider.get("base_url", "").rstrip("/")
    if provider.get("wire_api", "responses") != "responses":
        return None
    if base not in ("https://api.moonshot.cn/v1", "https://api.moonshot.ai/v1"):
        return None
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("Moonshot provider name must be a simple config key")
    return name, base


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the user's Authorization header to another origin.
        return None


def handler_for(upstream: str):
    base = urllib.parse.urlsplit(upstream)

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"  # close delimits SSE without buffering

        def log_message(self, *_args):
            pass  # no URLs, headers, prompts or credentials in access logs

        def do_GET(self):
            self.forward()

        def do_POST(self):
            self.forward()

        def forward(self):
            path = urllib.parse.urlsplit(self.path)
            if path.scheme or path.netloc or not path.path.startswith(base.path + "/"):
                self.send_error(404)
                return
            if self.headers.get("Upgrade") or self.headers.get("Transfer-Encoding"):
                self.send_error(400, "Only HTTP Responses requests are supported")
                return
            if self.headers.get("Content-Encoding", "identity") != "identity":
                self.send_error(415, "Encoded request bodies are not supported")
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 0:
                    raise ValueError
            except ValueError:
                self.send_error(400, "Invalid Content-Length")
                return
            body = self.rfile.read(size) if size else None
            if (
                body
                and self.command == "POST"
                and path.path
                in (
                    base.path + "/responses",
                    base.path + "/responses/compact",
                )
            ):
                body, count = normalize_request(body)
                if count:
                    print(
                        f"[moonshot-compat] removed_empty_assistant_messages={count}",
                        flush=True,
                    )
            connection_headers = {
                value.strip().lower()
                for value in self.headers.get("Connection", "").split(",")
            }
            excluded = (
                HOP_HEADERS
                | connection_headers
                | {"host", "content-length", "accept-encoding"}
            )
            headers = {
                k: v for k, v in self.headers.items() if k.lower() not in excluded
            }
            headers["Accept-Encoding"] = "identity"
            target = urllib.parse.urlunsplit(
                (base.scheme, base.netloc, path.path, path.query, "")
            )
            request = urllib.request.Request(
                target, data=body, headers=headers, method=self.command
            )
            try:
                # TLS verification is the stdlib default; no retries or model calls
                # beyond the one request already issued by Codex.
                response = urllib.request.build_opener(NoRedirect()).open(
                    request, timeout=300
                )
            except urllib.error.HTTPError as error:
                response = error
            except (OSError, urllib.error.URLError):
                self.send_error(502, "Moonshot transport unavailable")
                return
            try:
                with response:
                    self.send_response(response.status)
                    excluded = HOP_HEADERS | {
                        value.strip().lower()
                        for value in response.headers.get("Connection", "").split(",")
                    }
                    for name, value in response.headers.items():
                        if name.lower() not in excluded:
                            self.send_header(name, value)
                    self.end_headers()
                    while chunk := response.read1(65536):
                        self.wfile.write(chunk)
                        self.wfile.flush()
            except (OSError, urllib.error.URLError):
                # Closing the stream lets Codex report transport failure. Do not
                # append a second HTTP response or manufacture a completed turn.
                self.close_connection = True

    return Handler


def main() -> int:
    command = sys.argv[1:]
    if not command:
        raise SystemExit("usage: moonshot_responses.py codex app-server [arguments]")
    config_path = Path(os.environ.get("CODEX_HOME", "/data/codex")) / "config.toml"
    selected = selected_provider(tomllib.loads(config_path.read_text()))
    if selected is None:
        os.execvp(command[0], command)
    name, upstream = selected
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler_for(upstream))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    override_key = "model_providers." + name
    child = None

    def stop(signum, _frame):
        if child is not None:
            child.send_signal(signum)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        child = subprocess.Popen(
            command
            + [
                "-c",
                override_key
                + ".base_url="
                + json.dumps(f"http://127.0.0.1:{server.server_port}/v1"),
                "-c",
                override_key + ".supports_websockets=false",
            ]
        )
        return child.wait()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    sys.exit(main())
