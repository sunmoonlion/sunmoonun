"""A registered supplier query should have a durable, readable response."""
from test_durable_delivery_db import db
from test_source_query_db import need
from test_user_library_http import BASE, api


async def test_supplier_query_creation_returns_committed_list(api, db):
    from sqlalchemy import text

    client, _ = api
    try:
        response = await client.post(f"{BASE}/resolutions", json={
            "consumer": "expert:1", "contract_version": "data-request/v1",
            "needs": [need().as_dict()], "params": {"task_date": "2026-11-27"}
        })
    finally:
        async with db() as session:
            assert await session.scalar(text("SELECT count(*) FROM user_data_resolution")) == 1
    assert response.status_code == 201, response.text
    key = response.json()["items"][0]["key"]
    assert key["source_query"]["channel"] == "wind"
