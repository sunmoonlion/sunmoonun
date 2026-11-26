"""Exercise version selection and upload recovery via the user's library routes."""
import pytest
from test_library_web_http import CSV, WEB, _upload, api, db


async def test_nonexistent_version_zero_cannot_download_latest(api):
    client, _, _ = api
    mid = (await _upload(client))["material"]["material_id"]
    result = await client.get(f"{WEB}/materials/{mid}/versions/0/content")
    assert result.status_code in (404, 422)


async def test_post_commit_processing_failure_can_retry_without_second_material(api, monkeypatch):
    client, _, services = api
    real = services.library._add_processing

    async def transient(*args):
        raise ConnectionError("synthetic processing consent store outage")

    monkeypatch.setattr(services.library, "_add_processing", transient)
    params = {"name": "retry.csv", "process": True}
    with pytest.raises(ConnectionError):
        await client.post(f"{WEB}/materials", params=params, content=CSV)
    monkeypatch.setattr(services.library, "_add_processing", real)
    assert (await client.post(f"{WEB}/materials", params=params, content=CSV)).status_code == 201
    shelf = (await client.get(f"{WEB}/materials")).json()
    assert len(shelf) == 1


async def test_new_content_version_retry_preserves_one_revision(api, monkeypatch):
    client, _, services = api
    mid = (await _upload(client))["material"]["material_id"]
    path = f"{WEB}/materials/{mid}/versions"
    real = services.library._add_processing

    async def transient(*args):
        raise ConnectionError("synthetic processing consent store outage")

    monkeypatch.setattr(services.library, "_add_processing", transient)
    with pytest.raises(ConnectionError):
        await client.post(path, params={"process": True}, content=CSV + b"revision")
    monkeypatch.setattr(services.library, "_add_processing", real)
    assert (await client.post(path, params={"process": True}, content=CSV + b"revision")).status_code == 201
    versions = (await client.get(path)).json()
    assert [v["version_no"] for v in versions] == [1, 2]


async def test_completed_trade_replay_after_owner_lowers_license(api):
    from test_library_web_http import INTERNAL
    client, _, _ = api
    mid = (await _upload(client, license="sale", attest="true"))["material"]["material_id"]
    trade = {"seller": "alice", "buyer": "bob", "material_id": mid, "transaction_ref": "confirmed-trade"}
    first = await client.post(f"{INTERNAL}/purchases", json=trade)
    assert first.status_code == 201
    assert (await client.put(f"{WEB}/materials/{mid}/license", json={"license": "self"})).status_code == 200
    repeat = await client.post(f"{INTERNAL}/purchases", json=trade)
    assert repeat.status_code == 201 and repeat.json() == first.json()


async def test_public_delivery_returns_whether_this_call_created_version(api, monkeypatch):
    from test_library_web_http import INTERNAL
    from app.interfaces.endpoints import user_library_routes as routes
    client, state, _ = api
    state["service"] = "knowfeed"
    path = f"{INTERNAL}/service/public-originals"
    params = {"channel": "cninfo", "channel_doc_id": "same-report", "name": "report.csv",
              "subject": "600519.SH", "doc_type": "annual_report"}
    original = routes._existing_version
    receipts = []

    async def interleaved(*args):
        previous = await original(*args)
        monkeypatch.setattr(routes, "_existing_version", original)
        receipts.append((await client.post(path, params=params, content=CSV)).json())
        return previous

    monkeypatch.setattr(routes, "_existing_version", interleaved)
    receipts.append((await client.post(path, params=params, content=CSV)).json())
    assert len({row["material_id"] for row in receipts}) == 1
    assert [row["created"] for row in receipts].count(True) == 1
