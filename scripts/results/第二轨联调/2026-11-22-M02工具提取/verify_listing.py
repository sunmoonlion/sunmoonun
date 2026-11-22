"""Run the M02 case across three local PostgreSQL-backed services and the script worker image."""

import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack, asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit
from uuid import UUID, uuid4

from case import TOOLS, definition, identifier, source, suite

WORKSPACE = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(WORKSPACE / "sunmoonun/scripts/local-integration"))
from p1_author import BENCH, LAB, configure_lab

MART = WORKSPACE / "knowmart-app/knowmart-backend/app"


async def bench(send):
    import httpx
    from app.application.workbench.formal_test_runs import FormalExecutions
    from app.bootstrap.api import create_app
    from app.domain.workbench.registry_sources import SourceDraft
    from app.domain.workbench.script_contract_generated import ScriptContainerMeter
    from app.infrastructure.workbench.repository import WorkbenchRepository
    from app.interfaces.endpoints import knowbot_runtime_routes as routes
    from core.config import Settings
    from script_worker_support import run_script_image
    from test_capabilities_db import OWNER
    from test_formal_script_execution_db import TARIFF, Executor, script_setup
    from test_workbench_ledger_db import db

    class ScriptWorker(Executor):
        async def start(self, owner, run, body):
            result = await run_script_image(body)
            self.calls.append(run)
            self.receipts[run] = {"state": "finished", "result": result}
            start = datetime.now(UTC)
            self.meters[run] = ScriptContainerMeter(
                run_id=run,
                job_uid=uuid4(),
                pod_uid=uuid4(),
                container_id="local-test-meter",
                started_at=start,
                finished_at=start + timedelta(seconds=1),
            )

    async with AsyncExitStack() as stack:
        gen = db.__wrapped__()
        sessions = await anext(gen)
        stack.push_async_callback(gen.aclose)
        template, factory, conductor, executor = await script_setup(
            sessions, ScriptWorker(), registered=True
        )
        async with sessions() as sql:
            repo = WorkbenchRepository(sql)
            async with repo.transaction():
                for check, (name, _, _) in TOOLS.items():
                    await repo.register_direct_revision(
                        OWNER,
                        identifier(check, "source"),
                        1,
                        SourceDraft(
                            kind="script", name=name + ".py", content=source(check)
                        ),
                    )

        async def methods():
            async with sessions() as sql:
                yield factory(WorkbenchRepository(sql)).formal_sources

        async def executions():
            async with sessions() as sql:
                repo = WorkbenchRepository(sql)
                yield FormalExecutions(repo, factory(repo))

        app = create_app(Settings())
        app.dependency_overrides.update(
            {
                routes.formal_methods: methods,
                routes.formal_executions: executions,
                routes.require_testrun_service: lambda: SimpleNamespace(
                    caller="knowlab"
                ),
            }
        )
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) as client:
            send(
                {
                    "runner": template.execution.runner.model_dump(mode="json"),
                    "destination": TARIFF.destination,
                }
            )
            while line := await asyncio.to_thread(sys.stdin.readline):
                msg = json.loads(line)
                if "advance" in msg:
                    async with sessions() as sql:
                        await factory(WorkbenchRepository(sql)).reconcile_scripts()
                    await conductor.advance(msg["advance"])
                    send(len(executor.calls))
                else:
                    response = await client.request(**msg)
                    send([response.status_code, response.text])


async def mart(send):
    from app.domain.market import FormalSelfListingIn
    from tests.test_knowbot_repository_db import db
    from tests.test_market_db import Vault, World

    database = db.__wrapped__()
    sessions = await anext(database)
    try:
        world = World(sessions, Vault())
        send({})
        while line := await asyncio.to_thread(sys.stdin.readline):
            body = FormalSelfListingIn.model_validate(json.loads(line))
            async with sessions() as sql:
                receipt = await world.svc(sql).submit_formal_self(body)
            async with sessions() as sql:
                row = await world.svc(sql).repo.formal_listing(
                    UUID(receipt["listing_id"]), lock=False
                )
                assert row["status"] == "listed" and row["scope"] == "self"
                assert (
                    str(row["method_id"]) == str(body.reference.method_id)
                    and row["digest"] == body.reference.digest
                )
            send(receipt)
    finally:
        await database.aclose()


@asynccontextmanager
async def peer(name, backend, env):
    proc = await asyncio.create_subprocess_exec(
        str(backend / ".venv/bin/python"),
        __file__,
        name,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        limit=2**21,
        cwd=backend,
        env=env,
    )

    async def read():
        data = await asyncio.wait_for(proc.stdout.readline(), 90)
        if not data:
            raise RuntimeError(f"{name} exited before replying")
        return json.loads(data)

    async def rpc(message):
        proc.stdin.write((json.dumps(message) + "\n").encode())
        await proc.stdin.drain()
        return await read()

    try:
        yield await read(), rpc
    finally:
        proc.stdin.close()
        await proc.wait()


async def author():
    import httpx
    from app.application.services.formal_methods import FormalMethodService
    from app.application.services.knowbot_service import KnowbotCreationService
    from app.infrastructure.external.knowbot_clients import RuntimeTestClients
    from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
    from app.interfaces.endpoints import knowbot_routes as routes
    from app.main import app
    from tests.knowbot_fakes import FakeRuntime
    from tests.test_knowbot_clients import KNOWBENCH, FakeOidc
    from tests.test_knowbot_repository_db import db
    from tests.test_knowbot_workdraft_routes import WEB as HEADERS
    from tests.test_knowbot_workdraft_routes import WEB_SID

    keys = (
        "AGENT_TEST_DATABASE_URL",
        "DELIVERY_TEST_DATABASE_URL",
        "MARKET_TEST_DATABASE_URL",
    )
    urls = [urlsplit(os.environ[k]) for k in keys]
    if len({u.path for u in urls}) != 3 or any(
        u.hostname not in ("localhost", "127.0.0.1") or not u.path.endswith("_tests")
        for u in urls
    ):
        raise ValueError("Use three separate local *_tests databases")
    async with AsyncExitStack() as stack:
        ready, runtime_call = await stack.enter_async_context(
            peer("bench", BENCH, os.environ.copy())
        )
        _, market_call = await stack.enter_async_context(
            peer(
                "mart",
                MART,
                {**os.environ, "DELIVERY_TEST_DATABASE_URL": os.environ[keys[2]]},
            )
        )

        async def forward(req):
            code, body = await runtime_call(
                {
                    "method": req.method,
                    "url": str(req.url),
                    "headers": dict(req.headers),
                    "content": req.content.decode(),
                }
            )
            return httpx.Response(code, content=body)

        runtime = RuntimeTestClients(
            {
                **KNOWBENCH,
                "KNOWBENCH_INTERNAL_URL": "https://127.0.0.1/api/internal/v1/knowbot-runtime",
            },
            oidc_client=FakeOidc(),
            transport=httpx.MockTransport(forward),
        )
        database = db.__wrapped__()
        sessions = await anext(database)
        stack.push_async_callback(database.aclose)
        configure_lab(sessions, runtime, ["author"])

        async def methods():
            async with sessions() as sql:
                yield FormalMethodService(
                    SqlKnowlabRepository(sql),
                    runtime,
                    SimpleNamespace(formal_self_listing=market_call),
                )

        async def creation():
            async with sessions() as sql:
                yield KnowbotCreationService(SqlKnowlabRepository(sql), FakeRuntime())

        app.dependency_overrides[routes.service] = creation
        app.dependency_overrides[routes.formal_service] = methods
        client = await stack.enter_async_context(
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://testserver",
                headers=HEADERS,
                cookies={WEB_SID: "author"},
            )
        )

        async def call(method, path, **kwargs):
            response = await client.request(method, "/api/web/v1/" + path, **kwargs)
            if not response.is_success:
                raise RuntimeError((path, response.status_code, response.text[:1000]))
            return response.json()

        receipts = {}
        for check, (_, title, _) in TOOLS.items():
            req = (
                await call(
                    "POST",
                    "knowbot-requests",
                    json={
                        "title": title,
                        "mode": "self",
                        "runtime": "knowbench",
                        "consent_test_data": True,
                        "idea": {
                            "kind": "six_questions",
                            "answers": {
                                "solves": title,
                                "not_solves": "不取数",
                                "inputs": "人民币报表事实",
                                "steps": "按 M02 原式核对",
                                "outputs": "状态与差额",
                                "correctness": "核对人工预期",
                            },
                        },
                        "cases": [
                            {
                                "case_id": "equal",
                                "input": {"question": "核验平衡样例"},
                                "expectations": [
                                    {
                                        "artifact": "result",
                                        "path": "status",
                                        "kind": "equals",
                                        "value": "balanced",
                                    }
                                ],
                            }
                        ],
                    },
                )
            )["request_id"]
            path = "knowbot-requests/" + req
            sources = (await call("GET", path + "/formal-method-sources"))["items"]
            selected = next(
                s for s in sources if s["source"] == identifier(check, "source")
            )
            draft = {
                "definition": definition(check, selected, ready["destination"]),
                "source": selected,
                "allowed_callers": ["host"],
            }
            current = await call("GET", path + "/workdraft")
            saved = await call(
                "POST",
                path + "/workdraft/cells",
                json={
                    "revision": current["revision"],
                    "cells": [{"path": "formal_method", "value": draft}],
                },
            )
            run = str(uuid4())
            mid = identifier(check, "method")
            cmd = {"run_id": run, "request_id": req, "revision": saved["revision"]}
            prefix = f"method-units/{mid}/executions"
            await call(
                "POST",
                prefix,
                json={
                    **cmd,
                    "execution": {
                        "suite": suite(check),
                        "runner": ready["runner"],
                        "budget": {"limit": "10", "currency": "CNY"},
                        "timeout_seconds": 180,
                        "max_wait_seconds": 600,
                    },
                },
            )
            endpoint = prefix + "/" + run
            approvals = set()
            for _ in range(80):
                await runtime_call({"advance": run})
                result = await call("GET", endpoint, params={"request_id": req})
                if result["status"] == "passed":
                    break
                if result["status"] not in ("pending", "running", "waiting"):
                    raise RuntimeError(
                        (check, result["status"], str(result["cases"])[:1800])
                    )
                for action in result["actions"]:
                    decision = {
                        key: action[key]
                        for key in ("case_id", "repetition", "token", "subject_digest")
                    }
                    await call(
                        "POST",
                        endpoint + "/actions/" + action["call_id"],
                        json={**decision, "request_id": req, "decision": "accept"},
                    )
                    approvals.add(action["call_id"])
            assert result["status"] == "passed" and len(approvals) == len(
                suite(check)["cases"]
            )
            version_path = f"method-units/{mid}/formal-versions/1"
            frozen = await call(
                "PUT", version_path, json={**cmd, "visibility": "private"}
            )
            confirm = {"digest": frozen["digest"]}
            listing = await call("PUT", version_path + "/self-listing", json=confirm)
            assert listing == await call(
                "PUT", version_path + "/self-listing", json=confirm
            )
            assert listing["reference"] == {"method_id": mid, "version": 1, **confirm}
            receipts[check] = {
                "request_id": req,
                "run_id": run,
                "approvals": len(approvals),
                "source_digest": selected["digest"],
                "suite": result["suite"],
                "listing": listing,
            }
            print(
                check,
                listing["status"],
                listing["listing_id"],
                file=sys.stderr,
                flush=True,
            )
        print(json.dumps(receipts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    role = sys.argv[1] if len(sys.argv) > 1 else "author"
    backend = {"bench": BENCH, "mart": MART, "author": LAB}[role]
    sys.path[:0] = [str(backend), str(backend / "tests")]

    def send(obj):
        print(json.dumps(obj), flush=True)

    asyncio.run(
        {"bench": lambda: bench(send), "mart": lambda: mart(send), "author": author}[
            role
        ]()
    )
