"""同一 HTTP 摘要头在原件与按页读法上的可复算性。使用 KnowBase 的临时库 fixture。"""
from hashlib import sha256

from test_durable_delivery_db import db as db
from test_user_library_http import api as api
from test_user_library_http import test_run_grants_reads_outputs_and_processing as exercise


async def test_digest_header_on_delivered_bytes(api):
    client, _ = api
    matches = {}

    async def observe(response):
        if response.is_success and "X-Content-SHA256" in response.headers:
            kind = response.request.url.path.rsplit("/", 1)[-1]
            matches[kind] = sha256(await response.aread()).hexdigest() == response.headers["X-Content-SHA256"]

    client.event_hooks["response"].append(observe)
    await exercise(api)
    assert matches == {"content": True, "rendition": False}
