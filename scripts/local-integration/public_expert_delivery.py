"""Buyer acceptance for formal_market_delivery.py --expert, using disposable identities."""

import asyncio
import json
import sys
import os


async def qualify_buyer(directory, port, references, purchase):
    import httpx

    async with httpx.AsyncClient(
        base_url=f"https://127.0.0.1:{port}", verify=str(directory / "cert")
    ) as client:

        async def allowed(subject, pins=None):
            response = await client.post(
                "/api/internal/v1/knowmart/formal-methods/eligible",
                json={
                    "owner_subject": subject,
                    "references": references if pins is None else pins,
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
        if "--roundtrip" in sys.argv:
            while not (directory / "awaiting-upgrade").exists():
                await asyncio.sleep(0.1)
            revision = json.loads((directory / "awaiting-upgrade").read_text())
            assert await allowed("other", [revision]) == []
            await purchase(revision)
            assert await allowed("other", [revision]) == [revision]
            (directory / "upgraded").touch()
    while not (directory / "delivered").exists():
        await asyncio.sleep(0.1)


async def execute_buyer(directory, db, ctx, expert):
    from pytest import MonkeyPatch
    from test_capabilities_db import approval, body, service
    from test_ordinary_expert_execution_db import selected_match
    from test_source_licenses import license_record
    from test_workbench_task_runtime_db import drive
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
                incubations=getattr(ctx, "lab", None),
            ) as match:
                client, path, selected, runner, _, _ = match
                model = match[-1]

                async def adopted(origin, ref, proposal):
                    origin_path = "/api/workbench/find-expert/" + origin
                    shown = await client.get(origin_path + "/handoff/versions")
                    shown.raise_for_status()
                    choices = shown.json()
                    assert len(choices["options"]) == 1, choices
                    option = choices["options"][0]
                    assert option["candidate"]["reference"] == ref
                    if ref["version"] == 2:
                        assert option["changes"]["purpose"] == {
                            "before": choices["previous"]["declaration"]["purpose"],
                            "after": option["candidate"]["declaration"]["purpose"],
                        }
                    command = {
                        "review_digest": option["review_digest"],
                        "reference": ref,
                    }
                    responses = await asyncio.gather(
                        *(
                            client.put(origin_path + "/handoff/versions", json=command)
                            for _ in range(2)
                        )
                    )
                    responses[0].raise_for_status()
                    assert responses[0].json() == responses[1].json()
                    new_path = (
                        "/api/workbench/find-expert/" + responses[0].json()["task_id"]
                    )
                    assert new_path != origin_path
                    proposal["picks"][0]["reference"] = ref
                    model.replies.append(json.dumps(proposal))
                    await drive(runner)
                    new = (await client.get(new_path)).json()
                    assert new["followup"]["origin"] == origin, new
                    selected = {
                        "reference": ref,
                        "review_digest": new["formal"]["review_digest"],
                    }
                    (
                        await client.put(new_path + "/selection", json=selected)
                    ).raise_for_status()
                    return new_path, selected

                use_lab = hasattr(ctx, "lab")
                original_proposal = (await client.get(path)).json()["formal"]["match"]
                if use_lab and from_work:
                    path, selected = await adopted(
                        ctx.first_gap,
                        expert.reference.model_dump(mode="json"),
                        original_proposal,
                    )

                async def deliver(path, selected):
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
                        json={
                            "revision": 1,
                            "preview_digest": rejected["preview_digest"],
                        },
                    )
                    assert refusal.status_code == 409 and not ctx.remote.calls
                    binding.update(
                        expected_revision=1, values={"to": "test@example.test"}
                    )
                    (
                        await client.put(path + "/preparation", json=binding)
                    ).raise_for_status()
                    preview = (
                        await client.get(path + "/execution-preview?revision=2")
                    ).json()
                    assert not preview["issues"] and not preview["dispatch_gap"], (
                        preview
                    )
                    confirmed = await client.put(
                        path + "/execution",
                        json={
                            "revision": 2,
                            "preview_digest": preview["preview_digest"],
                        },
                    )
                    confirmed.raise_for_status()
                    replay = await client.put(
                        path + "/execution",
                        json={
                            "revision": 2,
                            "preview_digest": preview["preview_digest"],
                        },
                    )
                    assert replay.json() == confirmed.json() and not ctx.remote.calls
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
                            matched = await repo.get_task(
                                match_id, owner_actor_id=owner
                            )
                            origin = matched["original_input"]["input"][
                                "source_session"
                            ]
                            links = await repo.list_record_events(
                                session_id=origin, types=("expert/delegation",)
                            )
                            assert (
                                len(links) == 1
                                and links[0]["payload"]["match_task_id"] == match_id
                            )
                            assert (
                                links[0]["payload"]["project_id"]
                                == result["project_id"]
                            )
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
                    return task

                first_task = await deliver(path, selected)
                if use_lab:
                    gap = {
                        "review_digest": selected["review_digest"],
                        "reference": selected["reference"],
                        "gap": "Include the approved receipt in the next revision.",
                    }
                    transfer = await client.put(path + "/handoff", json=gap)
                    transfer.raise_for_status()
                    handoff = transfer.json()
                    assert handoff["mode"] == (
                        "author_revision" if from_work else "user_demand"
                    )
                    assert (
                        await client.put(path + "/handoff", json=gap)
                    ).json() == handoff
                    if from_work:
                        ctx.revision = await ctx.lab.freeze(
                            db, ctx, handoff["request_id"], 2
                        )
                    else:
                        assert (await client.get(path + "/handoff/versions")).json()[
                            "options"
                        ] == []
                        revision = ctx.revision.reference.model_dump(mode="json")
                        marker = directory / "upgrading"
                        marker.write_text(json.dumps(revision))
                        marker.replace(directory / "awaiting-upgrade")
                        while not (directory / "upgraded").exists():
                            await asyncio.sleep(0.1)
                        new_path, chosen = await adopted(
                            path.rsplit("/", 1)[-1], revision, original_proposal
                        )
                        assert (await client.get(path)).json()["execution"][
                            "task_id"
                        ] == first_task
                        ctx.remote.calls.clear()
                        second = await deliver(new_path, chosen)
                        assert second != first_task
                        async with db() as sql:
                            repo = WorkbenchRepository(sql)
                            for task_id, ref in [
                                (first_task, selected["reference"]),
                                (second, revision),
                            ]:
                                stored = await repo.get_task(
                                    task_id, owner_actor_id=owner
                                )
                                assert stored["pack_snapshot"]["reference"] == ref
                        from expert_duty_support import verify_period

                        await verify_period(
                            db,
                            patch,
                            client,
                            path,
                            (await client.get(path)).json(),
                            expert.reference,
                            owner=owner,
                        )
                        print(
                            "Verified gap, tool incubation, both expert freezes, buyer v2 and recurring use of the original v1."
                        )

    await exercise(ctx.owner, "author", ctx.factory, ctx.asset, True)
    (directory / "self-delivered").touch()
    while not (directory / "market-ready").exists():
        await asyncio.sleep(0.1)
    await exercise(OTHER, "other", factory, buyer_asset, False)
