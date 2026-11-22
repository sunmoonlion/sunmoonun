"""Single-task Responses endpoint for the isolated Codex worker."""

import http.client
import json
import os
import ssl
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from instruction_control import InstructionControl
from instruction_responses import ProviderAuthenticationRejected

BINDING = Path("/run/instruction")
MAX_BODY = 2 * 1024 * 1024


class Gateway(BaseHTTPRequestHandler):
    # Requests may contain private author inputs. Never send HTTP data to Pod logs.
    def log_message(self, *args):
        pass

    def setup(self):
        self.request.settimeout(15)
        super().setup()

    def do_POST(self):
        if self.path != "/v1/responses":
            self.send_error(404)
            return
        started = False

        def start():
            nonlocal started
            started = True
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()

        try:
            sizes = self.headers.get_all("Content-Length", [])
            if len(sizes) != 1 or self.headers.get("Transfer-Encoding"):
                raise ValueError
            size = int(sizes[0])
            if not 0 < size <= MAX_BODY:
                raise ValueError
            raw = self.rfile.read(size)
            if len(raw) != size:
                raise ValueError
            body = json.loads(raw)
            if not isinstance(body, dict):
                raise TypeError
            # Only the trusted host that received turn/start may set this file.
            # The first Codex POST can arrive before the Secret projection refresh.
            deadline = time.monotonic() + 90
            while not (turn := (BINDING / "turn").read_text().strip()):
                if time.monotonic() >= deadline:
                    raise TimeoutError
                time.sleep(0.25)
            self.server.control.relay(
                body, turn_id=turn, start=start, write=self.wfile.write
            )
        except ProviderAuthenticationRejected:
            self.send_error(401, "Model provider rejected its credential")
        except (ValueError, KeyError, TypeError, RecursionError, PermissionError):
            if not started:
                self.send_error(403)
        except (OSError, EOFError, http.client.HTTPException):
            if not started:
                self.send_error(503)


def main():
    if (BINDING / "uid").read_text().strip() != os.environ["POD_UID"]:
        raise SystemExit("Instruction binding belongs to another gateway")
    control = InstructionControl(
        os.environ["INSTRUCTION_CONTROL_ORIGIN"],
        gateway_uid=os.environ["POD_UID"],
        attempt_id=(BINDING / "attempt").read_text().strip(),
        ticket_file=BINDING / "ticket",
        credential_file="/run/provider/instruction-provider.json",
        receipt_dir="/proof",
        tls_context=ssl.create_default_context(
            cafile=os.environ.get("INSTRUCTION_CONTROL_CA")
        ),
    )
    # Acknowledgement retries consume only the original durable receipt.
    # A transient control failure also gets retried while the gateway is idle.
    server = HTTPServer(("0.0.0.0", 47801), Gateway)
    server.control = control
    server.timeout = 2
    next_check = 0.0
    while True:
        if not control.acknowledged and time.monotonic() >= next_check:
            next_check = time.monotonic() + 2
            try:
                control.reconcile()
            except (OSError, ValueError, http.client.HTTPException):
                pass
        server.handle_request()


if __name__ == "__main__":
    main()
