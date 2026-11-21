"""Trusted gateway client. Files are mounted only in the per-Attempt egress process."""

import http.client
import json
import os
import ssl
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

from instruction_responses import forward

MAX_REPLY = 2 * 1024 * 1024


class InstructionControl:
    def __init__(
        self,
        origin,
        *,
        gateway_uid,
        attempt_id,
        ticket_file,
        credential_file,
        receipt_dir,
        tls_context=None,
    ):
        target = urlsplit(origin)
        if (
            target.scheme != "https"
            or not target.hostname
            or target.username is not None
            or target.password is not None
            or target.path not in ("", "/")
            or target.query
            or target.fragment
        ):
            raise ValueError("Instruction control needs an internal HTTPS origin")
        self.host, self.port = target.hostname, target.port or 443
        self.gateway_uid = str(UUID(gateway_uid))
        self.attempt_id = str(UUID(attempt_id))
        self.proof = Path(receipt_dir) / (self.attempt_id + ".json")
        self.ticket_file = Path(ticket_file)
        self.credential_file = Path(credential_file)
        if tls_context is not None and (
            not tls_context.check_hostname
            or tls_context.verify_mode != ssl.CERT_REQUIRED
        ):
            raise ValueError(
                "Instruction control requires server certificate verification"
            )
        self.tls_context = tls_context
        self.acknowledged = False

    def _post(self, operation, payload):
        # Short-lived tickets can be renewed for the same bound gateway.
        ticket = self.ticket_file.read_text().strip()
        if not ticket or len(ticket) > 4096:
            raise ValueError("Missing instruction gateway ticket")
        conn = http.client.HTTPSConnection(
            self.host, self.port, timeout=15, context=self.tls_context
        )
        try:
            conn.request(
                "POST",
                "/api/internal/v1/instruction-control/" + operation,
                body=json.dumps(payload).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + ticket,
                    "X-Instruction-Gateway": self.gateway_uid,
                    "X-Instruction-Attempt": self.attempt_id,
                },
            )
            with conn.getresponse() as response:
                if response.status in (401, 403, 409):
                    raise PermissionError("Instruction control declined " + operation)
                if (
                    response.status != 200
                    or response.headers.get_content_type() != "application/json"
                ):
                    raise OSError("Instruction control unavailable for " + operation)
                raw = response.read(MAX_REPLY + 1)
                if len(raw) > MAX_REPLY:
                    raise ValueError("Instruction control reply exceeds the limit")
                return json.loads(raw)
        finally:
            conn.close()

    def retain_receipt(self, payload):
        # Write-once, across gateway processes. A crash before publishing a
        # complete record cannot leave a partially written receipt for replay.
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        with tempfile.NamedTemporaryFile(dir=self.proof.parent) as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
            try:
                os.link(stream.name, self.proof)
            except FileExistsError:
                if self.proof.read_bytes() != encoded:
                    raise ValueError(
                        "Conflicting instruction provider receipt"
                    ) from None
            directory = os.open(self.proof.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)

    def reconcile(self):
        """Replay only the original provider receipt, even after credential revocation."""
        try:
            payload = json.loads(self.proof.read_bytes())
        except FileNotFoundError:
            return False
        if self._post("receipt", payload) != {"recorded": True}:
            raise OSError("Instruction receipt was not acknowledged")
        self.acknowledged = True
        return True

    def relay(
        self, body, *, turn_id, start, write, connect=http.client.HTTPSConnection
    ):
        # Capture the whole credential file once per POST, including the key that
        # will actually be sent. Never source the credential id from the caller.
        provider = json.loads(self.credential_file.read_bytes())
        if body.get("model") != provider["model"]:
            raise PermissionError("Model differs from the loaded sandbox credential")

        def claim(raw, credential_id):
            decision = self._post(
                "claim",
                {
                    "credential_id": credential_id,
                    "provider": provider["provider"],
                    "endpoint": endpoint,
                    "turn_id": turn_id,
                    "body": raw,
                },
            )
            return decision["url"], decision["outgoing"]

        def receipt(response_id, usage):
            self.retain_receipt(
                {"turn_id": turn_id, "response_id": response_id, "usage": usage}
            )
            self.reconcile()

        endpoint = provider["base_url"].rstrip("/") + "/responses"
        forward(
            body,
            endpoint=endpoint,
            credential_id=provider["credential_id"],
            api_key=provider["key"],
            claim=claim,
            receipt=receipt,
            start=start,
            write=write,
            connect=connect,
        )
