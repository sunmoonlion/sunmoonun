"""Exercise KnowLab authoring and KnowBench on disposable *_tests PostgreSQL databases.

From the worktree root, export DELIVERY_TEST_DATABASE_URL and AGENT_TEST_DATABASE_URL
and run knowlab-app/knowlab-backend/app/.venv/bin/python sunmoonun/scripts/local-integration/p1_author.py.
The web component talks to a loopback KnowLab. The KnowLab runtime client sends its
HTTP requests to the real KnowBench routes in a separate interpreter. Only identity,
the installed MCP peer and the test computer use local fixtures.
"""

import asyncio
import json
import os
import re
import socket
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / "knowbench-app/knowbench-backend/app"
LAB = ROOT / "knowlab-app/knowlab-backend/app"
WEB = ROOT / "knowlab-app/knowlab-web-frontend/app"


def provisioner_revision():
    manifest = (
        ROOT / "sunmoonun/infrastructure/applications/component-images.yaml"
    ).read_text()
    section = manifest.split("  sandbox-provisioner:", 1)[1].split("  sandbox:", 1)[0]
    return re.search(r"^    revision: ([0-9a-f]{40})$", section, re.MULTILINE).group(1)


async def bench():
    import httpx
    from fastapi import Header
    from test_capabilities_db import OWNER
    from formal_plan_support import EchoRemote
    from test_formal_execution_db import setup
    from test_workbench_ledger_db import db
    from app.bootstrap.api import create_app
    from app.application.workbench.formal_test_runs import FormalExecutions
    from app.infrastructure.workbench.repository import WorkbenchRepository
    from app.interfaces.endpoints import knowbot_runtime_routes as routes
    from core.config import Settings

    schema = db.__wrapped__()
    sessions = await anext(schema)
    try:

        class ManifestPeer(EchoRemote):
            async def call(self, url, token, name, arguments):
                result = await super().call(url, token, name, arguments)
                revision = provisioner_revision()
                assert arguments["to"] in ("sandbox-provisioner", revision)
                result["structuredContent"] = {"receipt": revision}
                return result

        template, _, _, factory, conductor = await setup(
            sessions, remote=ManifestPeer()
        )

        async def methods():
            async with sessions() as session:
                yield factory(WorkbenchRepository(session)).formal_sources

        async def executions():
            async with sessions() as session:
                repo = WorkbenchRepository(session)
                yield FormalExecutions(repo, factory(repo))

        async def caller(authorization: str = Header()):
            assert authorization.startswith("Bearer token-")
            return SimpleNamespace(caller="knowlab")

        app = create_app(Settings())
        app.dependency_overrides.update(
            {
                routes.formal_methods: methods,
                routes.formal_executions: executions,
                routes.require_testrun_service: caller,
            }
        )
        print(json.dumps(template.model_dump(mode="json", by_alias=True)), flush=True)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="https://knowbench-tls.ns.svc.cluster.local",
        ) as client:
            for line in sys.stdin:
                req = json.loads(line)
                if "advance" in req:
                    await conductor.advance(req["advance"])
                    result = None
                elif "evidence" in req:
                    async with sessions() as session:
                        row = await WorkbenchRepository(session).formal_validation(
                            OWNER, req["evidence"]
                        )
                        result = row["execution_evidence"]["cases"][0]
                else:
                    reply = await client.request(**req)
                    result = [reply.status_code, reply.text]
                print(json.dumps(result, default=str), flush=True)
    finally:
        await schema.aclose()


async def author(peer, template):
    import httpx
    import uvicorn
    from sqlalchemy import text
    from app.application.services.formal_methods import FormalMethodService
    from app.application.services.knowbot_incubation import KnowbotIncubationService
    from app.application.services.knowbot_service import KnowbotCreationService
    from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
    from app.domain.knowbots.drafts import KnowbotRequestIn
    from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
    from app.infrastructure.external.knowbot_clients import RuntimeTestClients
    from app.interfaces.endpoints import knowbot_routes as routes
    from app.interfaces.http.middleware import auth
    from app.main import app
    from tests.knowbot_fakes import FakeRuntime, request_body
    from tests.test_knowbot_clients import FakeOidc, KNOWBENCH
    from tests.test_knowbot_repository_db import db
    from tests.test_auth_routes_security import FakeAuthService, session as login
    from tests.test_knowbot_workdraft_routes import WEB as HEADERS, WEB_SID

    lock = asyncio.Lock()

    async def rpc(message):
        async with lock:
            peer.stdin.write((json.dumps(message) + "\n").encode())
            await peer.stdin.drain()
            return json.loads(await asyncio.wait_for(peer.stdout.readline(), 30))

    review_requests = {}

    async def forward(request):
        code, body = await rpc(
            {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "content": request.content.decode(),
            }
        )
        if request.method == "POST" and request.url.path.endswith(
            ("/formal-method-validations", "/formal-method-executions")
        ):
            graph = json.loads(request.content)["draft"]["definition"]["procedure"]
            if "collaboration" in graph:
                assert code == 409 and json.loads(body)["code"] == "runtime_capability_gap"
                review_requests[request.url.path.rsplit("/", 1)[1]] = graph["collaboration"]
        if code >= 400:
            print(request.url.path, code, body[:1000], file=sys.stderr)
        return httpx.Response(code, content=body)

    runtime = RuntimeTestClients(
        {
            **KNOWBENCH,
            "KNOWBENCH_INTERNAL_URL": "https://127.0.0.1/api/internal/v1/knowbot-runtime",
        },
        oidc_client=FakeOidc(),
        transport=httpx.MockTransport(forward),
    )
    schema = db.__wrapped__()
    sessions = await anext(schema)
    try:

        async def sql():
            async with sessions() as session:
                yield session

        async def methods():
            async with sessions() as session:
                yield FormalMethodService(SqlKnowlabRepository(session), runtime)

        async def incubation():
            async with sessions() as session:
                yield KnowbotIncubationService(
                    SqlKnowlabRepository(session), None, FakeRuntime()
                )

        app.dependency_overrides[routes.incubation_service] = incubation
        user = login("web", "profile:read")
        user = user.model_copy(
            update={
                "principal": user.principal.model_copy(update={"subject": "author"})
            }
        )
        auth.web_auth_service = FakeAuthService({"author": user})
        routes.runtime_clients = lambda: runtime
        app.dependency_overrides.update(
            {routes.get_db_session: sql, routes.formal_service: methods}
        )
        async with sessions() as session:
            repo = SqlKnowlabRepository(session)
            creation = KnowbotCreationService(repo, FakeRuntime())

            async def new_request(title):
                return str(
                    (
                        await creation.submit(
                            "author",
                            KnowbotRequestIn.model_validate(request_body(title=title)),
                        )
                    ).id
                )

            leaf_request = await new_request("P1 provider")
            expert_request = await new_request("P1 expert")
            draft = template["draft"]
            declaration = draft["definition"]["capability_declaration"]
            declaration.update(
                title="Verify provisioner revision",
                purpose="Resolve and verify a pinned image build source",
            )
            draft["definition"]["access_requirements"][0]["resources"][0]["values"] = [
                "sandbox-provisioner",
                provisioner_revision(),
            ]
            for side in ("inputs", "outputs"):
                for slot in draft["definition"]["procedure"][side].values():
                    slot["meaning"] = {"unit": "image-build-reference"}
            await KnowbotWorkdraftService(repo).save(
                "author", leaf_request, revision=0, edits=[("formal_method", draft)]
            )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            headers=HEADERS,
            cookies={WEB_SID: "author"},
        ) as client:

            async def call(method, path, **kwargs):
                response = await client.request(method, "/api/web/v1/" + path, **kwargs)
                assert response.is_success, (path, response.status_code, response.text)
                return response.json()

            async def trial(mid, request_id, steps, cancel=False):
                import copy

                spec = copy.deepcopy(template["execution"])
                spec["suite"].pop("digest")
                spec["suite"]["suite_id"] = str(uuid4())
                spec["suite"]["cases"][0]["input"]["values"] = {
                    "to": "sandbox-provisioner"
                }
                spec["suite"]["cases"][0]["expected"]["assertions"][0]["value"] = (
                    provisioner_revision()
                )
                run = str(uuid4())
                command = {"request_id": request_id, "revision": 1, "run_id": run}
                prefix = f"method-units/{mid}/executions"
                await call("POST", prefix, json={**command, "execution": spec})
                endpoint = f"{prefix}/{run}"
                decisions = 0
                for _ in range(18):
                    await rpc({"advance": run})
                    result = await call(
                        "GET", endpoint, params={"request_id": request_id}
                    )
                    if result["status"] == "passed":
                        break
                    assert result["status"] in ("running", "pending", "waiting"), result
                    for action in result["actions"]:
                        if cancel and decisions == 1:
                            stopped = await call(
                                "POST",
                                endpoint + "/cancel",
                                json={"request_id": request_id},
                            )
                            assert stopped["status"] == "cancelled", stopped
                            return
                        fields = {
                            k: action[k]
                            for k in (
                                "case_id",
                                "repetition",
                                "token",
                                "subject_digest",
                            )
                        }
                        await call(
                            "POST",
                            endpoint + "/actions/" + action["call_id"],
                            json={
                                **fields,
                                "request_id": request_id,
                                "decision": "accept",
                            },
                        )
                        decisions += 1
                assert decisions == steps and result["status"] == "passed", result
                frozen = await call(
                    "PUT",
                    f"method-units/{mid}/formal-versions/1",
                    json={**command, "visibility": "private"},
                )
                assert frozen["definition"]["procedure"]["kind"] == (
                    "direct" if steps == 1 else "orchestration"
                )
                if steps == 2:
                    evidence = await rpc({"evidence": run})
                    assert evidence["validated"] and len(evidence["steps"]) == 2
                    first, second = evidence["steps"]
                    assert second["input_bindings"] == [
                        {"step_id": "prepare", **first["artifact"]}
                    ]
                    assert first["artifact"]["id"] != second["artifact"]["id"]
                    assert second["outputs"]["receipt"] == provisioner_revision()
                return frozen

            leaf_id, expert_id = str(uuid4()), str(uuid4())
            leaf = await trial(leaf_id, leaf_request, 1)
            wanted = draft["definition"]["procedure"]["inputs"]["to"]
            for mismatch in (
                {"meaning": {"unit": "other"}},
                {"schema": {"type": "integer"}},
            ):
                matches = await call(
                    "POST",
                    f"knowbot-requests/{expert_request}/incubation-tools/matching-outputs",
                    json={
                        "slot": {**wanted, **mismatch},
                        "exclude_method_id": expert_id,
                    },
                )
                assert matches["items"] == []
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                url = f"http://127.0.0.1:{sock.getsockname()[1]}"
                server = uvicorn.Server(
                    uvicorn.Config(app, lifespan="off", log_level="error")
                )
                serving = asyncio.create_task(server.serve(sockets=[sock]))
                try:
                    while not server.started:
                        if serving.done():
                            await serving
                        await asyncio.sleep(0.02)
                    child = await asyncio.create_subprocess_exec(
                        "pnpm",
                        "exec",
                        "vitest",
                        "run",
                        "tests/component/p1-live.test.tsx",
                        cwd=WEB,
                        env={
                            **os.environ,
                            "LUNA_P1_URL": url,
                            "LUNA_P1_REQUEST": expert_request,
                            "LUNA_P1_METHOD": expert_id,
                            "LUNA_P1_LEAF": leaf_id,
                        },
                    )
                    assert await child.wait() == 0, "author component failed"
                finally:
                    server.should_exit = True
                    await serving
            await trial(expert_id, expert_request, 2, cancel=True)
            expert = await trial(expert_id, expert_request, 2)
            async with sessions() as session:
                refs = (
                    (
                        await session.execute(
                            text(
                                "SELECT child_digest FROM method_dependencies WHERE method_id=:mid"
                            ),
                            {"mid": expert_id},
                        )
                    )
                    .scalars()
                    .all()
                )
                assert refs == [leaf["digest"]]
            from tests.test_knowbot_repository_db import _run, _versions

            migration = [
                p for p in _versions() if p.stem == "20261120_0028_method_graph_indexes"
            ]
            assert len(migration) == 1
            async with sessions() as session:
                async with session.begin():
                    connection = await session.connection()
                    await connection.run_sync(lambda c: _run(c, migration, "downgrade"))
                    await connection.run_sync(lambda c: _run(c, migration))
                    result = await session.execute(
                        text(
                            "SELECT v.digest,s.name FROM knowbot_method_version v JOIN method_version_slots s "
                            "USING (method_id,version) WHERE v.method_id=:mid AND s.direction='outputs'"
                        ),
                        {"mid": leaf_id},
                    )
                    assert result.all() == [(leaf["digest"], "receipt")]
                    deps = await session.execute(
                        text(
                            "SELECT child_digest FROM method_dependencies WHERE method_id=:mid"
                        ),
                        {"mid": expert_id},
                    )
                    assert deps.scalars().all() == [leaf["digest"]]
            path = f"knowbot-requests/{expert_request}/workdraft"
            saved = await call(
                "POST",
                path + "/cells",
                json={
                    "revision": 1,
                    "cells": [
                        {
                            "path": "collaboration",
                            "value": {
                                "prepare": {"isolation_group": "independent"},
                                "step_1": {
                                    "handoff_from": ["prepare"],
                                    "review_requirements": {"prepare": "different_model_family"},
                                },
                            },
                        }
                    ],
                },
            )
            assert saved["revision"] == 2
            reopened = await call("GET", path)
            assert reopened["body"]["collaboration"] == saved["body"]["collaboration"]
            assert {(g["step"], g["primitive"]) for g in reopened["runtime_gaps"]} == {
                ("prepare", "isolation_group"),
                ("step_1", "staged_handoff"),
                ("step_1", "isolated_reviewer"),
                ("step_1", "different_model_family"),
            }
            blocked = await client.post(
                f"/api/web/v1/method-units/{expert_id}/validations",
                json={
                    "request_id": expert_request,
                    "revision": 2,
                    "run_id": str(uuid4()),
                },
            )
            assert (
                blocked.status_code == 409
                and blocked.json()["code"] == "runtime_capability_gap"
            ), blocked.text
            spec = dict(template["execution"])
            spec["suite"] = {k: v for k, v in spec["suite"].items() if k != "digest"}
            refused_run = await client.post(
                f"/api/web/v1/method-units/{expert_id}/executions",
                json={
                    "request_id": expert_request,
                    "revision": 2,
                    "run_id": str(uuid4()),
                    "execution": spec,
                },
            )
            assert (
                refused_run.status_code == 409
                and refused_run.json()["code"] == "runtime_capability_gap"
            )
            assert review_requests == {
                endpoint: saved["body"]["collaboration"]
                for endpoint in ("formal-method-validations", "formal-method-executions")
            }
            print(
                "P1 verified: indexed retrieval, author adoption and reload, mid-run cancellation, two artifacts and frozen expert",
                expert["digest"],
            )
    finally:
        await schema.aclose()


async def main():
    peer = await asyncio.create_subprocess_exec(
        str(BENCH / ".venv/bin/python"),
        __file__,
        "--bench",
        cwd=BENCH,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        limit=2**20,
    )
    try:
        template = json.loads(await asyncio.wait_for(peer.stdout.readline(), 45))
        await author(peer, template)
    finally:
        peer.stdin.close()
        await asyncio.wait_for(peer.wait(), 30)


if __name__ == "__main__":
    provider = sys.argv[1:] == ["--bench"]
    root = BENCH if provider else LAB
    sys.path[:0] = [str(root), str(root / "tests")]
    asyncio.run(bench() if provider else main())
