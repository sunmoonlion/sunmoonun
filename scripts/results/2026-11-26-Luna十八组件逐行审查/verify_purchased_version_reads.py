"""在同一份资料上比较逐版格式核验与逐版下载。身份使用资料库 HTTP fixture。"""
from test_durable_delivery_db import db as db
from test_user_library_http import BASE, api as api
from app.domain.user_data import Owner


async def test_format_and_content_for_two_receipted_versions(api):
    client, state = api
    state["service"] = "knowmart"
    payloads = [b"year,value\n2024,10\n", b"year,value\n2025,20\n"]
    first = await client.post(
        BASE + "/materials", params={"name": "report.csv"}, content=payloads[0]
    )
    mid = first.json()["material"]["material_id"]
    root = f"{BASE}/materials/{mid}"
    license_result = await client.put(root + "/license", json={"license": "sale", "attest": True})
    assert license_result.status_code == 200
    for version in (1, 2):
        if version == 2:
            assert (await client.post(root + "/versions", content=payloads[1])).status_code == 201
        receipt = await client.post(BASE + "/purchases", json={
            "seller": "alice", "material_id": mid, "buyer": "bob", "transaction_ref": f"receipt-{version}"
        })
        assert receipt.status_code == 201 and receipt.json()["version_no"] == version
    state["owner"] = Owner("bob", "knowbench")
    assert (await client.post(root + "/uses", json={"use": "app:knowbench"})).status_code == 201
    downloads = []
    for version in (1, 2):
        path = f"{root}/versions/{version}"
        assert (await client.get(path + "/format")).status_code == 200
        content = await client.get(path + "/content")
        if content.status_code == 200:
            assert content.content == payloads[version - 1]
        else:
            assert content.json()["code"] == "version_not_found"
        downloads.append(content.status_code)
    assert sorted(downloads) == [200, 404]
