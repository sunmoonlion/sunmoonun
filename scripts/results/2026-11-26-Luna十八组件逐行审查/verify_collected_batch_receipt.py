"""同一采集交付的第二位描述有误，修订后再次发送。仅使用隔离测试夹具。"""
import json

from test_collection_boundaries_db import beneficiaries, params
from test_durable_delivery_db import db as db
from test_library_web_http import INTERNAL, api as api


async def test_partial_receipt_and_source_change(api):
    client, state, services = api
    state["service"] = "knowfeed"
    first = beneficiaries()[0]
    second = {**first, "subject": "bob"}
    old, corrected = b"year,value\n2024,1", b"year,value\n2024,2"

    async def send(row, content):
        return await client.post(
            INTERNAL + "/service/collected-originals", params=params(),
            files={"file": ("report.csv", content)},
            data={"beneficiaries": json.dumps([first, row])},
        )

    invalid = {**second, "prefill": {**second["prefill"], "doc_type": "missing_type"}}
    rejected = await send(invalid, old)
    assert rejected.status_code == 422
    assert len(await services.library.shelf("alice")) == 1
    assert not await services.library.shelf("bob")

    retry = await send(second, corrected)
    assert retry.status_code == 201
    copies = {}
    for row in retry.json():
        _, content = await services.library.download(row["subject"], "knowbench", row["material_id"], row["version_no"])
        copies[row["subject"]] = content
    assert copies == {"alice": old, "bob": corrected}
