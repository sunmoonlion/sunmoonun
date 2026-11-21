"""One isolated Responses POST. Control callbacks belong to the trusted trial host."""

import http.client
import json
from urllib.parse import urlsplit

# A malformed/truncated stream must leave the reservation pending.
MAX_EVENT = 2 * 1024 * 1024


class ProviderAuthenticationRejected(Exception):
    """The pinned upstream returned HTTP 401 before starting a model stream."""


def forward(
    body,
    *,
    endpoint,
    credential_id,
    api_key,
    claim,
    receipt,
    start,
    write,
    connect=http.client.HTTPSConnection,
):
    """Claim before connecting. Never redirect, reconnect or retry a submitted request."""
    target = urlsplit(endpoint)
    if (
        target.scheme != "https"
        or not target.hostname
        or target.username is not None
        or target.password is not None
        or target.query
        or target.fragment
        or not target.path.endswith("/responses")
    ):
        raise ValueError("Expected a pinned HTTPS Responses endpoint")
    authorized_url, outgoing = claim(body, credential_id)
    if authorized_url != endpoint:
        raise ValueError("Sandbox endpoint differs from the authorized route")
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Accept-Encoding": "identity",
    }
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    upstream = connect(target.hostname, target.port or 443, timeout=120)
    try:
        upstream.request(
            "POST", target.path, body=json.dumps(outgoing).encode(), headers=headers
        )
        with upstream.getresponse() as response:
            if response.status == 401:
                raise ProviderAuthenticationRejected
            if (
                response.status != 200
                or response.headers.get_content_type() != "text/event-stream"
            ):
                raise ValueError("Provider returned no Responses event stream")
            # Keep collecting usage if the client leaves after upstream dispatch.
            connected = True
            try:
                start()
            except OSError:
                connected = False
            lines = []
            size = 0
            response_id = None
            while True:
                line = response.readline(MAX_EVENT + 1)
                size += len(line)
                if size > MAX_EVENT:
                    raise ValueError("Provider event exceeds the stream limit")
                if line.rstrip(b"\r\n"):
                    if line.startswith(b"data:"):
                        lines.append(line[5:].lstrip(b" "))
                else:
                    data = b"".join(lines).strip()
                    if data and data != b"[DONE]":
                        event = json.loads(data)
                        kind = event.get("type")
                        record = event.get("response") or {}
                        if kind == "response.created":
                            response_id = record.get("id")
                        elif kind in (
                            "response.completed",
                            "response.incomplete",
                            "response.failed",
                        ):
                            if not response_id or record.get("id") != response_id:
                                raise ValueError(
                                    "Provider completion lacks its original response identity"
                                )
                            if record.get("usage") is not None:
                                receipt(response_id, record["usage"])
                    size, lines = 0, []
                if not line:
                    break
                if connected:
                    try:
                        write(line)
                    except OSError:
                        connected = False
    finally:
        upstream.close()
