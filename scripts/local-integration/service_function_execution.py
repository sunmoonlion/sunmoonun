"""Run using KnowBench pytest and two disposable *_tests database URLs.

The two backend applications run in separate interpreters. Only the HTTP wire
uses an in-process transport on each side of the subprocess pipe.
"""

import asyncio
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "knowbase-app/knowbase-backend/app"
BENCH = ROOT / "knowbench-app/knowbench-backend/app"


async def provider():
    import httpx
    from app.application.services.data_query_revisions import function_revision
    from app.domain.user_library import PUBLIC_OWNER
    from app.domain.user_runs import GrantRequestItem, InputPin
    from app.interfaces.http.internal.function_calls import build_function_router
    from core.config import Settings
    from fastapi import FastAPI
    from test_durable_delivery_db import db
    from test_registered_data_functions import World

    schema = db.__wrapped__()
    sessions = await anext(schema)
    try:
        world = World(sessions)
        material, version = await world.publish()

        async def grant(ref):
            return await world.runs.grant_by_user(
                "author",
                "knowbench",
                "delegation",
                ref,
                [
                    GrantRequestItem(
                        InputPin(material.id, 1, version.sha256), "public", PUBLIC_OWNER
                    )
                ],
            )

        await grant("native-comparison")
        setup = json.loads(sys.stdin.readline())
        name = setup["name"]
        query = setup["query"]
        field = setup["field"]
        if name == "read_facts":
            sample = await world.facts(sub="author", run="native-comparison")
            query = {"refs": [row["ref"] for row in sample["facts"]]}
        expected = (
            await world.facts(
                name=name,
                **query,
                sub="author",
                scope="run",
                run="native-comparison",
            )
        )[field]
        if field == "passages":
            assert expected[0]["source"]["page"] == 88
        elif field == "inputs":
            assert len(expected) == 1 and expected[0]["material_id"] == material.id
            assert expected[0]["version_no"] == 1
        else:
            rows = expected if field == "facts" else expected[0]["inputs"]
            assert {r["code"] for r in rows} == {"IS.REVENUE", "IS.COST"} and {
                r["source"]["page"] for r in rows
            } == {88}
        if field == "values":
            from decimal import Decimal

            assert Decimal(expected[0]["value"]) == Decimal("0.8")
        settings = Settings(
            knowbase_mcp_jwt_public_key=setup["public"],
            knowbase_mcp_jwt_issuer="knowbench",
        )
        app = FastAPI()
        app.include_router(
            build_function_router(settings, world.functions), prefix="/api"
        )
        chat = await world.runs.register_session("author", "knowbench")
        print(
            json.dumps(
                [
                    function_revision(name),
                    expected,
                    chat.id,
                    query,
                    function_revision("read_input"),
                    material.id,
                ]
            ),
            flush=True,
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://localhost"
        ) as http:
            for line in sys.stdin:
                msg = json.loads(line)
                if "grant" in msg:
                    reply = (await grant(msg["grant"])).id
                elif "catalog_sample" in msg:
                    sample, _ = await world.lib.upload("author", "shown.txt", b"shared")
                    await world.lib.show("author", sample.id, "app:knowbench")
                    await world.lib.upload("author", "hidden.txt", b"hidden")
                    reply = [
                        sample.id,
                        [
                            function_revision(op)
                            for op in ("lookup", "describe_items", "list_library")
                        ],
                    ]
                elif "revoke_task_grant" in msg:
                    await world.runs.revoke_by_user("author", msg["revoke_task_grant"])
                    reply = True
                elif "readers" in msg:
                    reply = [
                        r["reader"]
                        for r in await world.runs.reads(PUBLIC_OWNER, material.id)
                    ]
                elif "prepare_text" in msg:
                    from datetime import date

                    job = await world.runs.issue_processing(
                        "knowfeed", PUBLIC_OWNER, material.id, 1
                    )
                    await world.runs.write_rendition(
                        "knowfeed",
                        job.id,
                        "text",
                        "test-reader",
                        ("中文🙂" * 21000).encode(),
                        title="脚本分页",
                        published_on=date(2026, 1, 1),
                    )
                    reply = True
                elif "revoke_chat" in msg:
                    [active] = await world.runs.session_grants(
                        "author", "knowbench", chat.id
                    )
                    await world.runs.revoke_by_user("author", active.id)
                    reply = True
                else:
                    res = await http.post(
                        msg["path"],
                        json=msg["body"],
                        headers={"Authorization": msg["auth"]},
                    )
                    reply = [res.status_code, res.text, dict(res.headers)]
                print(json.dumps(reply), flush=True)
    finally:
        await schema.aclose()


if __name__ == "__main__":
    sys.path[:0] = [str(BASE), str(BASE / "tests")]
    asyncio.run(provider())
else:
    sys.path[:0] = [str(BENCH), str(BENCH / "tests")]
    from test_workbench_ledger_db import db as db  # noqa: PLC0414 (pytest fixture)
    from test_workbench_mcp_routes import (
        served as served,  # noqa: PLC0414 (pytest fixture)
    )


@pytest.mark.parametrize("scene", ["chat", "work"])
@pytest.mark.parametrize(
    "name,field,query",
    [
        ("query_facts", "facts", {}),
        ("read_facts", "facts", {}),
        ("list_inputs", "inputs", {}),
        ("search_evidence", "passages", {"query": "渠道库存"}),
        ("query_metric", "values", {"metric": "gross_margin"}),
    ],
)
async def test_registered_function_and_expert_with_actual_knowbase(
    db, served, monkeypatch, scene, name, field, query
):
    import httpx
    from app.application.workbench.tokens import TokenIssuer, generate_private_key_pem
    from app.domain.workbench.service_functions import FunctionRevision
    from test_formal_function_db import exercise_function

    issuer = TokenIssuer(generate_private_key_pem(), issuer="knowbench")
    process = await asyncio.create_subprocess_exec(
        str(BASE / ".venv/bin/python"),
        __file__,
        cwd=BASE,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        limit=2 * 1024 * 1024,  # One JSON line may carry a full Unicode material page.
    )

    async def exchange(msg):
        process.stdin.write((json.dumps(msg) + "\n").encode())
        await process.stdin.drain()
        line = await asyncio.wait_for(process.stdout.readline(), timeout=45)
        assert line, "KnowBase fixture stopped"
        return json.loads(line)

    try:
        (
            revision,
            expected,
            chat,
            query,
            material_revision,
            material_id,
        ) = await exchange(
            {
                "public": issuer.public_pem(),
                "name": name,
                "field": field,
                "query": query,
            }
        )

        async def forward(req):
            status, body, headers = await exchange(
                {
                    "path": req.url.path,
                    "body": json.loads(req.content),
                    "auth": req.headers["Authorization"],
                }
            )
            return httpx.Response(status, content=body, headers=headers)

        async def grant(ref):
            await exchange({"grant": ref})

        await exercise_function(
            db,
            FunctionRevision.model_validate(revision),
            issuer,
            expected,
            forward=forward,
            grant=grant,
            query=query,
            output_name=field,
        )
        from app.application.workbench.session_service import SessionService
        from app.infrastructure.external.knowbase_data_v2 import KnowbaseDataV2
        from app.infrastructure.workbench.repository import WorkbenchRepository
        from app.infrastructure.workbench.service_functions import register_revision
        from app.interfaces.endpoints.workbench_routes import token_issuer
        from app.interfaces.mcp import workbench_mcp
        from sqlalchemy import text
        from test_workbench_ledger_db import OWNER, seed
        from test_workbench_mcp_routes import URL, bearer, tool
        from tool_invocation_support import ObservedPlatformTransport

        async with db() as session:
            await register_revision(
                session, FunctionRevision.model_validate(material_revision)
            )
        _, _, sid = await seed(db)
        if scene == "chat":
            async with db() as session:
                sid = (
                    await SessionService(WorkbenchRepository(session)).start(
                        owner_actor_id=OWNER, kind="chat"
                    )
                )["session_id"]
        async with db() as session, session.begin():
            assert (await WorkbenchRepository(session).get_session(sid))[
                "kind"
            ] == scene
            await session.execute(
                text(
                    "UPDATE workbench_sessions SET knowbase_session_id=:chat, knowbase_session_expires_at=now()+interval '1 hour' WHERE id=:sid"
                ),
                {"chat": chat, "sid": sid},
            )
        served.dependency_overrides[token_issuer] = lambda: issuer
        client = KnowbaseDataV2(
            {"KNOWBASE_INTERNAL_URL": "https://localhost"},
            transport=httpx.MockTransport(forward),
        )
        if name == "read_facts":
            from decimal import Decimal

            from app.application.workbench.run_reader import RunReader
            from app.domain.workbench.errors import ComputeRefused, UserDataUnavailable
            from test_method_plans_db import task as create_task

            tid, _ = await create_task(db)
            grant_id = await exchange({"grant": tid})
            reader = RunReader(client, issuer)
            async with db() as session:
                repo = WorkbenchRepository(session)
                async with repo.transaction():
                    await repo.insert_task_resolution(
                        {
                            "task_id": tid,
                            "resolution_id": tid,
                            "revision": 1,
                            "consumer": "expert:fixture@1",
                            "params": {},
                            "grant_ref": tid,
                            "status": "ready",
                        }
                    )
                task_row = await repo.get_task(tid)
                with pytest.raises(ComputeRefused, match="registered read contract"):
                    await reader.facts(repo, task_row, [])
                values = await reader.facts(repo, task_row, query["refs"])
                assert values == {r["ref"]: Decimal(r["value"]) for r in expected}
                reads = await repo.list_task_calls(OWNER, tid)
                [read] = [
                    r
                    for r in reads
                    if r["detail"].get("identity_basis") == "host_task_data_read"
                ]
                assert (
                    read["detail"]["function_receipt"]["digest"] == revision["digest"]
                )
                assert "function:" + read["id"] in await exchange({"readers": True})

                async def lost_receipt(req):
                    valid = await forward(req)
                    assert valid.status_code == 200
                    return httpx.Response(200, json=valid.json() | {"digest": ""})

                uncertain = RunReader(
                    KnowbaseDataV2(
                        {"KNOWBASE_INTERNAL_URL": "https://localhost"},
                        transport=httpx.MockTransport(lost_receipt),
                    ),
                    issuer,
                )
                with pytest.raises(UserDataUnavailable, match="confirm the result"):
                    await uncertain.facts(repo, task_row, query["refs"])
                ledger = await repo.list_task_calls(OWNER, tid)
                [unknown] = [c for c in ledger if c["status"] == "unknown"]
                assert "function_receipt" not in unknown["detail"]
                assert "function:" + unknown["id"] in await exchange({"readers": True})
                quote = {
                    "material_id": material_id,
                    "page": 88,
                    "text": "报告期内渠道库存保持合理水平",
                }
                assert await reader.quotes(
                    repo, task_row, [quote, quote | {"page": 1}]
                ) == [{"found": True}, {"found": False, "reason": "not_found"}]
                await exchange({"revoke_task_grant": grant_id})
                assert await reader.quotes(repo, task_row, [quote]) == [
                    {"found": False, "reason": "page_not_readable"}
                ]
                with pytest.raises(ComputeRefused, match="no such fact"):
                    await reader.facts(repo, task_row, query["refs"])
        monkeypatch.setattr(workbench_mcp, "knowbase_v2", lambda: client)
        async with httpx.AsyncClient(
            transport=ObservedPlatformTransport(
                served, db, {"current": sid, "chat": sid}
            ),
            base_url="http://testserver",
        ) as native:

            async def ask(**args):
                res = await native.post(
                    URL, headers=bearer(issuer=issuer), json=tool(name, **query, **args)
                )
                return res.json()["result"]

            if name == "search_evidence":
                shown, revisions = await exchange({"catalog_sample": True})
                for row in revisions:
                    async with db() as session:
                        await register_revision(
                            session, FunctionRevision.model_validate(row)
                        )

                async def direct(operation, **args):
                    response = await native.post(
                        URL, headers=bearer(issuer=issuer), json=tool(operation, **args)
                    )
                    return response.json()["result"]

                vocabulary = await direct("describe_items")
                assert not vocabulary["isError"], vocabulary
                assert vocabulary["structuredContent"]["metrics"]
                located = await direct(
                    "lookup",
                    subject="600519.SH",
                    doc_type="annual_report",
                    period_start="2025-01-01",
                    period_end="2025-12-31",
                )
                assert located["structuredContent"] == {
                    "status": "shown",
                    "zone": "public",
                }
                library = await direct("list_library", conversation=sid)
                assert [
                    m["material_id"] for m in library["structuredContent"]["materials"]
                ] == [shown]
                assert (await direct("list_library", session=chat))["isError"]
                assert (
                    await direct(
                        "lookup",
                        subject="600519.SH",
                        doc_type="annual_report",
                        run="native-comparison",
                    )
                )["isError"]
            unread = (await ask(conversation=sid))["structuredContent"]
            assert unread[field] == []
            if name == "read_facts":
                assert unread["not_found"] == query["refs"]
            read = await native.post(
                URL,
                headers=bearer(issuer=issuer),
                json=tool(
                    "read_input",
                    conversation=sid,
                    what="pages",
                    material_id=material_id,
                    version_no=1,
                    page_from=88,
                    page_to=88,
                ),
            )
            selected = read.json()["result"]
            assert selected["isError"] is False, selected
            assert selected["structuredContent"]["pages"] == [
                {"page": 88, "text": "报告期内渠道库存保持合理水平，营业收入同比增长。"}
            ]
            assert "function:" + selected["_meta"]["call_id"] in await exchange(
                {"readers": True}
            )
            found = await ask(conversation=sid)
            assert found["structuredContent"][field] == expected
            call_id = found["_meta"]["call_id"]
            readers = await exchange({"readers": True})
            assert ("function:" + call_id in readers) == (name != "list_inputs")
            async with db() as session:
                detail = await session.scalar(
                    text("SELECT detail FROM workbench_calls WHERE id=:cid"),
                    {"cid": call_id},
                )
                assert (
                    detail["operation"]["registered_source"]["digest"]
                    == revision["digest"]
                )
            assert (await ask(conversation=sid, run="native-comparison"))["isError"]
            market = await ask(scope="market")
            if name in ("list_inputs", "search_evidence"):
                assert market["isError"]
            else:
                assert market["structuredContent"][field] == expected
            assert await exchange({"revoke_chat": True})
            assert (await ask(conversation=sid))["structuredContent"][field] == []
            async with db() as session, session.begin():
                await session.execute(
                    text(
                        "DELETE FROM workbench_registry_service_functions WHERE provider='knowbase' AND name=:name AND version=1"
                    ),
                    {"name": name},
                )
            missing = await ask(scope="market")
            assert (
                missing["isError"] and "not registered" in missing["content"][0]["text"]
            )
        if name == "read_facts":
            await exchange({"prepare_text": True})
            await verify_script_pages(
                db, issuer, client, exchange, chat, material_id, revoke=scene == "chat"
            )
    finally:
        process.stdin.close()
        await process.stdin.wait_closed()
        assert await asyncio.wait_for(process.wait(), timeout=45) == 0


async def verify_script_pages(
    db, issuer, client, exchange, chat, material_id, *, revoke
):
    import base64
    from datetime import UTC, datetime, timedelta

    from app.infrastructure.workbench.repository import WorkbenchRepository
    from sqlalchemy import text
    from test_capabilities_db import approval, service
    from test_skill_execution_db import setup
    from test_workbench_ledger_db import OWNER
    from tool_invocation_support import request_call

    sid, executor, _, key, token = await setup(db)

    async def prepare(owner, call_id, body):
        if revoke:
            await exchange({"revoke_chat": True})

    executor.prepare = prepare
    async with db() as session:
        repo = WorkbenchRepository(session)
        async with repo.transaction():
            await repo.set_knowbase_session(
                sid, chat, datetime.now(UTC) + timedelta(minutes=5)
            )
        svc = service(repo)
        svc.script_executor = executor
        svc.script_material_source = (client, issuer)
        args = {
            "path": "scripts/calculate.py",
            "inputs": [
                {
                    "kind": "material",
                    "name": "input.txt",
                    "material_id": material_id,
                    "version_no": 1,
                    "reading": "text/1",
                }
            ],
        }
        staged = await request_call(svc, sid, token, key, args)
        script = await repo.capability_call(OWNER, staged["call_id"])
        result = await svc.decide(OWNER, script["id"], approval(script))
        rows = (
            (
                await session.execute(
                    text(
                        "SELECT id, status, detail FROM workbench_calls WHERE parent_call_id=:parent"
                    ),
                    {"parent": script["id"]},
                )
            )
            .mappings()
            .all()
        )
        readers = await exchange({"readers": True})
        confirmed = [r for r in rows if r["status"] == "succeeded"]
        assert all(
            "function:" + str(r["id"]) in readers
            and r["detail"]["operation"]["registered_source"]["name"] == "read_input"
            for r in confirmed
        )
        if revoke:
            assert len(confirmed) == 2 and len(rows) == 3
            assert result["status"] == "failed" and not executor.started
        else:
            assert len(confirmed) == len(rows) == 4
            assert result["status"] == "dispatching"
            [uploaded] = executor.started[0][2]["inputs"]
            assert (
                base64.b64decode(uploaded["data_base64"]) == ("中文🙂" * 21000).encode()
            )
