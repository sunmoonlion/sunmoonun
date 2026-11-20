"""Run the cross-author P1 from author UI through KnowLab, KnowMart and KnowBench.

Use the KnowLab backend interpreter. AGENT_TEST_DATABASE_URL (Bench),
DELIVERY_TEST_DATABASE_URL (Lab) and MARKET_TEST_DATABASE_URL (Mart) must refer
to separate disposable PostgreSQL databases on loopback. Service traffic uses
verified local TLS. Identities, the test computer and the MCP peer are fixtures.
"""

import asyncio
import copy
import json
import os
import socket
import subprocess
import sys
import tempfile
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit
from uuid import UUID, uuid4

from p1_author import BENCH, LAB, ROOT, WEB, configure_lab

MART = ROOT / "knowmart-app/knowmart-backend/app"
SCRIPT = Path(__file__).resolve()


def relation(target, name, url):
    prefix = target.upper() + "_" + name.upper().replace("-", "_") + "_SERVICE_"
    return {
        target.upper() + "_INTERNAL_URL": url,
        prefix + "CLIENT_ID": "fixture",
        prefix + "CLIENT_SECRET": "fixture-only",
        prefix + "SCOPE": target + ":" + name,
        prefix + "DISCOVERY_URL": "https://issuer.invalid/discovery",
        prefix + "BACKCHANNEL_ENDPOINT": "https://issuer.invalid/token",
    }


@asynccontextmanager
async def server(app, sock, tls=False):
    import uvicorn

    config = (
        {
            "ssl_certfile": os.environ["SSL_CERT_FILE"],
            "ssl_keyfile": os.environ["P1_TLS_KEY"],
        }
        if tls
        else {}
    )
    instance = uvicorn.Server(
        uvicorn.Config(app, lifespan="off", log_level="error", **config)
    )
    task = asyncio.create_task(instance.serve(sockets=[sock]))
    try:
        while not instance.started:
            if task.done():
                await task
                raise RuntimeError("server did not start")
            await asyncio.sleep(0.02)
        yield
    finally:
        instance.should_exit = True
        await task


async def serve_commands(app, ready, handle):
    with socket.socket(fileno=int(os.environ["P1_LISTENER"])) as sock:
        async with server(app, sock, True):
            print(json.dumps(ready), flush=True)
            while line := await asyncio.to_thread(sys.stdin.readline):
                result = await handle(json.loads(line))
                print(json.dumps(result), flush=True)


async def bench():
    from app.application.workbench.formal_test_runs import FormalExecutions
    from app.application.workbench.test_runs import KnowbotTestConductor
    from app.bootstrap.api import create_app
    from app.bootstrap.workbench import workbench_stores
    from app.domain.workbench.source_licenses import SourceLicenseCatalog
    from app.infrastructure.external.knowmart_client import KnowmartSummonClient
    from app.infrastructure.workbench.repository import WorkbenchRepository
    from app.interfaces.endpoints import knowbot_runtime_routes as routes
    from core.config import Settings
    from fastapi import Header
    from formal_plan_support import EchoRemote
    from test_capabilities_db import body, service
    from test_formal_execution_db import setup
    from test_source_licenses import license_record
    from test_workbench_ledger_db import OTHER, db, seed

    class Oidc:
        async def exchange_client_credentials(self, **kwargs):
            return {"access_token": "fixture-bench-to-mart", "expires_in": 300}

    market = KnowmartSummonClient(oidc_client=Oidc())
    remote = EchoRemote()
    case = {
        "case_id": "echo",
        "input": {"values": {"to": "test@example.test"}},
        "repetitions": 1,
        "minimum_passes": 1,
        "expected": {
            "outcome": "succeeded",
            "assertions": [
                {"kind": "equals", "pointer": "/receipt", "value": "test@example.test"}
            ],
        },
    }
    async with AsyncExitStack() as stack:
        database = db.__wrapped__()
        stack.push_async_callback(database.aclose)
        sessions = await anext(database)
        template, _, _, original, _ = await setup(
            sessions, cases=[case], remote=remote, public_review=True
        )
        env, _, _ = await seed(sessions, owner=OTHER)
        src = template.draft.source.model_dump(mode="json")
        rights = SourceLicenseCatalog(
            (
                license_record(src, rights={"execute": True, "deliver": True}),
                license_record(src, subject="other", record_id="buyer-test"),
            )
        )

        def factory(repo):
            caps = original(repo)
            caps.formal_sources.source_licenses = rights
            caps.formal_sources.market = market
            return caps

        async with sessions() as sql:
            repo = WorkbenchRepository(sql)
            asset = await service(repo).create_connection(
                OTHER, body().model_copy(update={"token": "fixture-consumer"})
            )
            buyer_source = (await factory(repo).formal_sources.sources("other"))[
                "items"
            ][0]
            assert (
                buyer_source["asset_id"] == asset["id"]
                and buyer_source["asset_id"] != src["asset_id"]
            )

        async def methods():
            async with sessions() as sql:
                yield factory(WorkbenchRepository(sql)).formal_sources

        async def executions():
            async with sessions() as sql:
                repo = WorkbenchRepository(sql)
                yield FormalExecutions(repo, factory(repo))

        async def lab(authorization: str = Header()):
            assert authorization == "Bearer token-1"
            return SimpleNamespace(caller="knowlab")

        async def mart(authorization: str = Header()):
            assert authorization == "Bearer fixture-mart-to-bench"
            return SimpleNamespace(caller="knowmart")

        app = create_app(Settings())
        app.dependency_overrides.update(
            {
                routes.formal_methods: methods,
                routes.formal_executions: executions,
                routes.require_testrun_service: lab,
                routes.require_method_delivery_service: mart,
            }
        )
        conductor = KnowbotTestConductor(
            workbench_stores(sessions), formal_capabilities=factory
        )

        async def handle(msg):
            if "advance" in msg:
                await conductor.advance(msg["advance"])
                return
            if "audit" in msg:
                async with sessions() as sql:
                    repo = WorkbenchRepository(sql)
                    evidence = (await repo.formal_validation(OTHER, msg["audit"]))[
                        "execution_evidence"
                    ]["cases"][0]
                    calls = await repo.list_task_calls(OTHER, msg["task"])
                    leaves = [row for row in calls if row["kind"] == "tool"]
                    assert len(leaves) == 2 and all(
                        str(r["source_asset_id"]) == asset["id"] for r in leaves
                    )
                    assert evidence["validated"] and len(evidence["steps"]) == 2
                    first, second = evidence["steps"]
                    assert second["input_bindings"] == [
                        {"step_id": "prepare", **first["artifact"]}
                    ]
                    assert first["artifact"]["id"] != second["artifact"]["id"]
                    assert second["outputs"]["receipt"] == "test@example.test"
            return {
                "dispatches": len(remote.calls),
                "buyer_dispatches": sum(
                    call[1] == "fixture-consumer" for call in remote.calls
                ),
            }

        await serve_commands(
            app,
            {
                "template": template.model_dump(mode="json", by_alias=True),
                "buyer_source": buyer_source,
                "env": env,
            },
            handle,
        )


async def mart():
    from app.domain.market import FormalListingIn, IncubationPermission, ReviewDecision
    from app.infrastructure.external.formal_method_delivery import FormalMethodDelivery
    from app.infrastructure.external.service_client import ServiceClient
    from app.infrastructure.security.relation_auth import require_summon_service
    from app.interfaces.endpoints import knowbot_routes
    from app.main import app
    from fastapi import Header
    from tests.test_knowbot_repository_db import db
    from tests.test_knowbot_routes import _caller
    from tests.test_market_db import Vault, World, approved_publisher

    async def token(self):
        return "fixture-mart-to-bench"

    ServiceClient.token = token

    async def caller(authorization: str = Header()):
        assert authorization == "Bearer fixture-bench-to-mart"
        return _caller("knowbench")

    async with AsyncExitStack() as stack:
        database = db.__wrapped__()
        stack.push_async_callback(database.aclose)
        sessions = await anext(database)
        world = World(sessions, Vault())
        await approved_publisher(world, subject="author")

        @asynccontextmanager
        async def market():
            async with sessions() as sql:
                svc = world.svc(sql)
                svc.public_market = True
                svc.formal_delivery = FormalMethodDelivery()
                yield svc

        async def service():
            async with market() as svc:
                yield svc

        app.dependency_overrides.update(
            {knowbot_routes.market_for_request: service, require_summon_service: caller}
        )

        async def handle(msg):
            async with market() as svc:
                if "publish" in msg:
                    listing = await svc.submit_formal(
                        "author",
                        FormalListingIn(
                            reference=msg["publish"], category="tools.office"
                        ),
                    )
                    lid = UUID(listing["listing_id"])
                    await svc.review_formal("ops", lid, ReviewDecision(approve=True))
                    return str(lid)
                if "acquire" in msg:
                    return (await svc.acquire_formal("other", UUID(msg["acquire"])))[
                        "reference"
                    ]
                return (
                    await svc.permit_incubation(
                        "author",
                        UUID(msg["listing"]),
                        IncubationPermission(scope=msg["scope"]),
                    )
                )["scope"]

        await serve_commands(app, {}, handle)


async def rpc(proc, msg):
    proc.stdin.write((json.dumps(msg) + "\n").encode())
    await proc.stdin.drain()
    return json.loads(await asyncio.wait_for(proc.stdout.readline(), 30))


async def exercise(runtime_peer, market_peer, ready):
    import httpx
    from app.application.services.knowbot_service import KnowbotCreationService
    from app.domain.knowbots.drafts import KnowbotRequestIn
    from app.infrastructure.external.knowbot_clients import RuntimeTestClients
    from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
    from app.main import app
    from sqlalchemy import text
    from tests.knowbot_fakes import FakeRuntime, request_body
    from tests.test_knowbot_clients import FakeOidc
    from tests.test_knowbot_repository_db import db
    from tests.test_knowbot_workdraft_routes import WEB as HEADERS
    from tests.test_knowbot_workdraft_routes import WEB_SID

    template = ready["template"]
    async with AsyncExitStack() as stack:
        database = db.__wrapped__()
        stack.push_async_callback(database.aclose)
        sessions = await anext(database)
        configure_lab(
            sessions, RuntimeTestClients(oidc_client=FakeOidc()), ["author", "other"]
        )

        async def project(subject, title):
            async with sessions() as sql:
                svc = KnowbotCreationService(SqlKnowlabRepository(sql), FakeRuntime())
                return str(
                    (
                        await svc.submit(
                            subject,
                            KnowbotRequestIn.model_validate(request_body(title=title)),
                        )
                    ).id
                )

        async def client(subject):
            return await stack.enter_async_context(
                httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app),
                    base_url="http://testserver/api/web/v1/",
                    headers=HEADERS,
                    cookies={WEB_SID: subject},
                )
            )

        seller, buyer = await client("author"), await client("other")

        async def send(c, path, payload):
            response = await c.post(path, json=payload)
            assert response.is_success, (path, response.status_code, response.text)
            return response.json()

        async def trial(c, mid, project_id, visibility, spec, *, shared_listing=None):
            run = str(uuid4())
            cmd = {"request_id": project_id, "run_id": run, "revision": 1}
            prefix = f"method-units/{mid}/executions"
            await send(c, prefix, {**cmd, "execution": spec})
            for _ in range(18):
                await rpc(runtime_peer, {"advance": run})
                response = await c.get(
                    f"{prefix}/{run}", params={"request_id": project_id}
                )
                response.raise_for_status()
                result = response.json()
                if result["status"] == "passed":
                    break
                assert result["status"] in ("running", "waiting", "pending"), result
                for action in result["actions"]:
                    await send(
                        c,
                        f"{prefix}/{run}/actions/{action['call_id']}",
                        {
                            **{
                                k: action[k]
                                for k in (
                                    "case_id",
                                    "repetition",
                                    "token",
                                    "subject_digest",
                                )
                            },
                            "request_id": project_id,
                            "decision": "accept",
                        },
                    )
            assert result["status"] == "passed", result
            version_path = f"method-units/{mid}/formal-versions/1"
            freeze = {**cmd, "visibility": visibility}
            if shared_listing is not None:
                await rpc(market_peer, {"listing": shared_listing, "scope": "none"})
                blocked = await c.put(version_path, json=freeze)
                assert (
                    blocked.status_code == 404
                    and blocked.json()["code"] == "method_not_found"
                ), blocked.text
                assert (await c.get(version_path)).status_code == 404
                await rpc(market_peer, {"listing": shared_listing, "scope": "acquired"})
            response = await c.put(version_path, json=freeze)
            assert response.is_success, response.text
            if shared_listing is not None:
                await rpc(
                    runtime_peer, {"audit": run, "task": result["cases"][0]["task_id"]}
                )
            return response.json()

        spec = copy.deepcopy(template["execution"])
        spec["suite"].pop("digest")
        publisher = await project("author", "Public P1 predecessor")

        def path(pid):
            return f"knowbot-requests/{pid}/workdraft/cells"

        await send(
            seller,
            path(publisher),
            {
                "revision": 0,
                "cells": [{"path": "formal_method", "value": template["draft"]}],
            },
        )
        published = await trial(
            seller, template["method_id"], publisher, "public", spec
        )
        public_ref = {k: published[k] for k in ("method_id", "version", "digest")}
        local_draft = copy.deepcopy(template["draft"])
        local_draft["source"] = ready["buyer_source"]
        local_draft["definition"]["capability_declaration"]["title"] = (
            "Buyer-owned delivery"
        )
        target, expert_id = str(uuid4()), str(uuid4())
        own, expert = (
            await project("other", "Own downstream"),
            await project("other", "P1 with acquired predecessor"),
        )
        await send(
            buyer,
            path(own),
            {"revision": 0, "cells": [{"path": "formal_method", "value": local_draft}]},
        )
        buyer_spec = copy.deepcopy(spec)
        buyer_spec["runner"]["environment_id"] = ready["env"]
        buyer_spec["suite"]["suite_id"] = str(uuid4())
        private = await trial(buyer, target, own, "private", buyer_spec)
        own_ref = {k: private[k] for k in public_ref}

        async def matches():
            reply = await send(
                buyer,
                f"knowbot-requests/{expert}/incubation-tools/matching-outputs",
                {
                    "directory": "shared",
                    "after": None,
                    "exclude_method_id": expert_id,
                    "slot": local_draft["definition"]["procedure"]["inputs"]["to"],
                },
            )
            return [row["reference"] for row in reply["items"]]

        listing = await rpc(market_peer, {"publish": public_ref})
        await rpc(market_peer, {"listing": listing, "scope": "acquired"})
        assert await matches() == []
        assert await rpc(market_peer, {"acquire": listing}) == public_ref
        assert await matches() == [public_ref]
        before = await rpc(runtime_peer, {"counts": True})
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            async with server(app, sock):
                ui = await asyncio.create_subprocess_exec(
                    "pnpm",
                    "exec",
                    "vitest",
                    "run",
                    "tests/component/p1-live.test.tsx",
                    "-t",
                    "indexed P1 bridge plan",
                    cwd=WEB,
                    env={
                        **os.environ,
                        "LUNA_P1_REQUEST": expert,
                        "LUNA_P1_METHOD": expert_id,
                        "LUNA_P1_LEAF": target,
                        "LUNA_P1_SHARED": public_ref["method_id"],
                        "LUNA_P1_URL": f"http://127.0.0.1:{sock.getsockname()[1]}",
                    },
                )
                try:
                    assert await asyncio.wait_for(ui.wait(), 90) == 0
                finally:
                    if ui.returncode is None:
                        ui.kill()
                        await ui.wait()
        assert await rpc(runtime_peer, {"counts": True}) == before
        await rpc(market_peer, {"listing": listing, "scope": "none"})
        assert await matches() == []
        denied = await buyer.post(
            f"method-units/{expert_id}/executions",
            json={
                "request_id": expert,
                "revision": 1,
                "run_id": str(uuid4()),
                "execution": buyer_spec,
            },
        )
        assert (
            denied.status_code == 404 and denied.json()["code"] == "method_not_found"
        ), denied.text
        assert await rpc(runtime_peer, {"counts": True}) == before
        await rpc(market_peer, {"listing": listing, "scope": "acquired"})
        buyer_spec["suite"]["suite_id"] = str(uuid4())
        frozen = await trial(
            buyer, expert_id, expert, "private", buyer_spec, shared_listing=listing
        )
        assert [
            s["candidates"] for s in frozen["definition"]["procedure"]["steps"]
        ] == [[public_ref], [own_ref]]
        after = await rpc(runtime_peer, {"counts": True})
        assert (
            after["buyer_dispatches"] - before["buyer_dispatches"]
            == after["dispatches"] - before["dispatches"]
            == 2
        )
        async with sessions() as sql:
            rows = (
                await sql.execute(
                    text(
                        "SELECT child_id,child_version,child_digest FROM method_dependencies WHERE method_id=:mid"
                    ),
                    {"mid": expert_id},
                )
            ).all()
            assert {(str(i), v, d) for i, v, d in rows} == {
                (r["method_id"], r["version"], r["digest"])
                for r in (public_ref, own_ref)
            }
        print(
            "Verified acquired predecessor, revocation before trial and freeze, two consumer-account dispatches, artifact handoff and two frozen dependency locks."
        )


@asynccontextmanager
async def worker(name, cwd, sock, env):
    proc = await asyncio.create_subprocess_exec(
        str(cwd / ".venv/bin/python"),
        str(SCRIPT),
        name,
        cwd=cwd,
        env={**env, "P1_LISTENER": str(sock.fileno())},
        pass_fds=(sock.fileno(),),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    try:
        ready = json.loads(await asyncio.wait_for(proc.stdout.readline(), 60))
        yield proc, ready
    finally:
        proc.stdin.close()
        try:
            code = await asyncio.wait_for(proc.wait(), 15)
        except TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        if code:
            raise RuntimeError(f"{name} exited with {code}")


async def main():
    urls = []
    for key in (
        "DELIVERY_TEST_DATABASE_URL",
        "AGENT_TEST_DATABASE_URL",
        "MARKET_TEST_DATABASE_URL",
    ):
        url = urlsplit(os.environ[key])
        if url.hostname not in ("localhost", "127.0.0.1") or not url.path.endswith(
            "_tests"
        ):
            raise ValueError(f"{key} must identify a disposable loopback test database")
        urls.append(url.path)
    if len(set(urls)) != 3:
        raise ValueError("Use three separate test databases")
    with (
        tempfile.TemporaryDirectory() as directory,
        socket.socket() as bs,
        socket.socket() as ms,
    ):
        for sock in (bs, ms):
            sock.bind(("127.0.0.1", 0))
        cert, key = (str(Path(directory) / n) for n in ("cert", "key"))
        await asyncio.to_thread(
            subprocess.run,
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-subj",
                "/CN=localhost",
                "-addext",
                "subjectAltName=IP:127.0.0.1",
                "-days",
                "1",
                "-keyout",
                key,
                "-out",
                cert,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        bench_url = (
            f"https://127.0.0.1:{bs.getsockname()[1]}/api/internal/v1/knowbot-runtime"
        )
        mart_url = f"https://127.0.0.1:{ms.getsockname()[1]}/api/internal/v1/knowmart"
        os.environ.update(
            relation("knowbench", "testrun", bench_url),
            SSL_CERT_FILE=cert,
            P1_TLS_KEY=key,
            NO_PROXY="127.0.0.1,localhost",
            no_proxy="127.0.0.1,localhost",
        )
        async with AsyncExitStack() as stack:
            mp, _ = await stack.enter_async_context(
                worker(
                    "mart",
                    MART,
                    ms,
                    {
                        **os.environ,
                        **relation("knowbench", "method-delivery", bench_url),
                        "DELIVERY_TEST_DATABASE_URL": os.environ[
                            "MARKET_TEST_DATABASE_URL"
                        ],
                    },
                )
            )
            bp, ready = await stack.enter_async_context(
                worker(
                    "bench",
                    BENCH,
                    bs,
                    {**os.environ, **relation("knowmart", "summon", mart_url)},
                )
            )
            await exercise(bp, mp, ready)


if __name__ == "__main__":
    role = sys.argv[1] if len(sys.argv) > 1 else "lab"
    root = {"bench": BENCH, "lab": LAB, "mart": MART}[role]
    sys.path[:0] = [str(root), str(root / "tests")]
    asyncio.run({"bench": bench, "mart": mart, "lab": main}[role]())
