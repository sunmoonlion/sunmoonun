"""Buyer acceptance for formal_market_delivery.py --expert, using disposable identities."""

import asyncio
import os


async def qualify_buyer(directory, port, references, purchase):
    import httpx

    async with httpx.AsyncClient(
        base_url=f"https://127.0.0.1:{port}", verify=str(directory / "cert")
    ) as client:

        async def allowed(subject):
            response = await client.post(
                "/api/internal/v1/knowmart/formal-methods/eligible",
                json={
                    "owner_subject": subject,
                    "references": references,
                    "include_acquired": True,
                },
            )
            response.raise_for_status()
            return response.json()["allowed"]

        for ref in references:
            listed = await client.post(
                "/api/internal/v1/knowmart/formal-methods/self-listings",
                json={
                    "owner_subject": "author",
                    "reference": ref,
                    "title": "Test method",
                    "purpose": "Return a receipt",
                    "review_findings": [],
                },
            )
            listed.raise_for_status()
            assert (
                listed.json()["status"] == "listed" and listed.json()["scope"] == "self"
            )
        assert {r["digest"] for r in await allowed("author")} == {
            r["digest"] for r in references
        }
        assert await allowed("other") == []
        marker = directory / "self-starting"
        marker.write_text(str(port))
        marker.replace(directory / "self-ready")
        while not (directory / "self-delivered").exists():
            await asyncio.sleep(0.1)
        await purchase(references[0])
        assert await allowed("other") == references[:1]
        await purchase(references[1])
        assert {r["method_id"] for r in await allowed("other")} == {
            r["method_id"] for r in references
        }
        assert await allowed("nonbuyer") == []
    marker = directory / "market-starting"
    marker.write_text(str(port))
    marker.replace(directory / "market-ready")
    while not (directory / "delivered").exists():
        await asyncio.sleep(0.1)


async def execute_buyer(directory, db, ctx, expert):
    from pytest import MonkeyPatch
    from test_capabilities_db import approval, body, service
    from test_ordinary_expert_execution_db import selected_match
    from test_source_licenses import license_record
    from test_workbench_advisor_db import drive
    from test_workbench_knowmart_client import ENV, FakeOidc
    from test_workbench_ledger_db import OTHER, seed

    from app.domain.workbench.source_licenses import SourceLicenseCatalog
    from app.infrastructure.external.knowmart_client import KnowmartSummonClient
    from app.infrastructure.workbench.repository import WorkbenchRepository

    while not (directory / "self-ready").exists():
        await asyncio.sleep(0.1)
    port = (directory / "self-ready").read_text()
    os.environ["SSL_CERT_FILE"] = str(directory / "cert")
    market = KnowmartSummonClient(
        {
            **ENV,
            "KNOWMART_INTERNAL_URL": f"https://127.0.0.1:{port}/api/internal/v1/knowmart",
        },
        oidc_client=FakeOidc(),
    )
    await seed(db, owner=OTHER)
    async with db() as session:
        repo = WorkbenchRepository(session)
        buyer_asset = await service(repo).create_connection(
            OTHER, body().model_copy(update={"token": "buyer-only-token"})
        )
    assert buyer_asset["id"] != ctx.asset["id"]
    source = ctx.leaf.draft.source.model_dump(mode="json")
    buyer_license = license_record(source, subject="other", record_id="buyer")

    def factory(repo):
        caps = ctx.factory(repo)
        caps.formal_sources.source_licenses = SourceLicenseCatalog((buyer_license,))
        return caps

    async def exercise(owner, subject, caps_factory, asset, from_work):
        ctx.remote.calls.clear()
        with MonkeyPatch.context() as patch:
            async with selected_match(
                db,
                patch,
                expert,
                None,
                owner,
                caps_factory,
                market=market,
                subject=subject,
                from_work=from_work,
            ) as match:
                client, path, selected, runner, _, _ = match
                prep = (await client.get(path + "/preparation")).json()
                accounts = {
                    k: options[0]["pin"]
                    for k, options in prep["account_options"].items()
                }
                assert accounts and all(
                    pin["asset_id"] == asset["id"] for pin in accounts.values()
                )
                binding = {
                    "expected_revision": 0,
                    "review_digest": selected["review_digest"],
                    "budget_limit": "1",
                    "values": {"to": "buyer@example.test"},
                    "accounts": accounts,
                    "materials": {},
                }
                (
                    await client.put(path + "/preparation", json=binding)
                ).raise_for_status()
                rejected = (
                    await client.get(path + "/execution-preview?revision=1")
                ).json()
                assert any(
                    issue["code"] == "operation_unverified"
                    for issue in rejected["issues"]
                )
                refusal = await client.put(
                    path + "/execution",
                    json={"revision": 1, "preview_digest": rejected["preview_digest"]},
                )
                assert refusal.status_code == 409 and not ctx.remote.calls
                binding.update(expected_revision=1, values={"to": "test@example.test"})
                (
                    await client.put(path + "/preparation", json=binding)
                ).raise_for_status()
                preview = (
                    await client.get(path + "/execution-preview?revision=2")
                ).json()
                assert not preview["issues"] and not preview["dispatch_gap"], preview
                confirmed = await client.put(
                    path + "/execution",
                    json={"revision": 2, "preview_digest": preview["preview_digest"]},
                )
                confirmed.raise_for_status()
                task = confirmed.json()["task_id"]
                for step in range(2):
                    await drive(runner)
                    async with db() as session:
                        repo = WorkbenchRepository(session)
                        attempts = await repo.list_attempts(task)
                        assert len(attempts) == step + 1, attempts
                        call = await repo.capability_call(
                            owner, attempts[-1]["refs"]["capability_call_id"]
                        )
                        assert call["status"] == "awaiting_approval"
                    assert len(ctx.remote.calls) == step
                    decision = await client.post(
                        f"/api/workbench/capability-calls/{call['id']}/decision",
                        json=approval(call).model_dump(mode="json"),
                    )
                    decision.raise_for_status()
                await drive(runner)
                result = (await client.get(path)).json()
                assert result["execution_state"] == "SUCCEEDED" and result[
                    "delivery"
                ] == {"final_receipt": "test@example.test"}, result
                if from_work:
                    async with db() as session:
                        repo = WorkbenchRepository(session)
                        match_id = path.rsplit("/", 1)[-1]
                        matched = await repo.get_task(match_id, owner_actor_id=owner)
                        origin = matched["original_input"]["input"]["source_session"]
                        links = await repo.list_record_events(
                            session_id=origin, types=("expert/delegation",)
                        )
                        assert (
                            len(links) == 1
                            and links[0]["payload"]["match_task_id"] == match_id
                        )
                        assert links[0]["payload"]["project_id"] == result["project_id"]
                        assert all(
                            step["reference"]
                            == ctx.leaf.reference.model_dump(mode="json")
                            for step in preview["steps"]
                        )
                        assert (
                            await repo.get_artifact(
                                task_id=task, name="expert_delivery", version=1
                            )
                        )["content"] == result["delivery"]
                    print(
                        "Verified self-listed expert, work conversation and final delivery."
                    )
                else:
                    assert [call[1] for call in ctx.remote.calls] == [
                        "buyer-only-token"
                    ] * 2
                    print(
                        "Verified buyer acquisitions, two buyer approvals and final artifact."
                    )

    await exercise(ctx.owner, "author", ctx.factory, ctx.asset, True)
    (directory / "self-delivered").touch()
    while not (directory / "market-ready").exists():
        await asyncio.sleep(0.1)
    await exercise(OTHER, "other", factory, buyer_asset, False)
