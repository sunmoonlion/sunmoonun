"""Exercise KnowLab authoring and KnowBench on disposable *_tests PostgreSQL databases.

From the worktree root, export DELIVERY_TEST_DATABASE_URL and AGENT_TEST_DATABASE_URL
and run knowlab-app/knowlab-backend/app/.venv/bin/python sunmoonun/scripts/local-integration/p1_author.py.
The web component talks to a loopback KnowLab. The KnowLab runtime client sends its
HTTP requests to the real KnowBench routes in a separate interpreter. Header probes use
the KnowBase HTTP API with a synthetic CSV and disposable database schema. Identity,
object storage, the installed MCP peer and the test computer use local fixtures.
Pass --registered-script to run the author chain using an owner-registered script
and the local isolated worker image, including a two-branch P2 join. Container timing uses a metering fixture.
"""

import asyncio
import copy
import hashlib
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


async def bench(registered_script=False):
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

        if registered_script:
            from script_worker_support import run_script_image
            from test_formal_script_execution_db import Executor, script_setup

            class LocalScript(Executor):
                async def start(self, owner, run, body):
                    result = await run_script_image(body)
                    await super().start(owner, run, body)
                    self.receipts[run]["result"] = result

            template, factory, conductor, _ = await script_setup(
                sessions, LocalScript(), registered=True
            )
        else:
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
        fixture = template.model_dump(mode="json", by_alias=True)
        if registered_script:
            from app.domain.workbench.registry_sources import SourceDraft

            code = """import json, os
from pathlib import Path
args = json.loads((Path(os.environ["SUNMOON_INPUT_DIR"])/"arguments.json").read_text())
result = {"receipt": args["to"] + "|" + args["other"], "assessment": "Author requests a second look"}
(Path(os.environ["SUNMOON_OUTPUT_DIR"])/"result.json").write_text(json.dumps(result))
"""
            async with sessions() as session:
                repo = WorkbenchRepository(session)
                source_id = uuid4()
                async with repo.transaction():
                    await repo.register_direct_revision(
                        OWNER, source_id, 1, SourceDraft(kind="script", name="join.py", content=code)
                    )
                available = await factory(repo).formal_sources.sources(template.owner_subject)
                fixture["join_source"] = next(
                    x for x in available["items"]
                    if x["kind"] == "registered_script" and x["source"] == str(source_id)
                )
        print(json.dumps(fixture), flush=True)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="https://knowbench-tls.ns.svc.cluster.local",
        ) as client:
            for line in sys.stdin:
                req = json.loads(line)
                if "advance" in req:
                    if registered_script:
                        async with sessions() as session:
                            await factory(WorkbenchRepository(session)).reconcile_scripts()
                    await conductor.advance(req["advance"])
                    result = None
                elif "receive_concurrently" in req:
                    path = f"https://127.0.0.1/api/internal/v1/knowbot-runtime/formal-method-executions/{req['receive_concurrently']}/step-deliveries"
                    async def receive(subject):
                        return await client.post(
                            path, params={"owner_subject": subject}, json=req["body"],
                            headers={"Authorization": "Bearer token-local"},
                        )
                    other = await receive("other-author")
                    assert other.status_code == 404, (other.status_code, other.text)
                    first, retry = await asyncio.gather(receive("author"), receive("author"))
                    assert first.status_code == retry.status_code == 200
                    assert first.json() == retry.json()
                    result = first.json()
                elif "review_counters" in req:
                    from sqlalchemy import text
                    async with sessions() as session:
                        result = list((await session.execute(text(
                            "SELECT (SELECT count(*) FROM workbench_tasks), "
                            "(SELECT count(*) FROM workbench_attempts), "
                            "(SELECT count(*) FROM workbench_calls)"
                        ))).one())
                elif "review_as_other" in req:
                    path = f"https://127.0.0.1/api/internal/v1/knowbot-runtime/formal-method-executions/{req['review_as_other']}/branch-review"
                    response = await client.post(path, params={"owner_subject": "other-author"}, json=req["body"],
                                                 headers={"Authorization": "Bearer token-local"})
                    result = response.status_code
                elif "purge" in req:
                    async with sessions() as session:
                        repo = WorkbenchRepository(session)
                        async with repo.transaction():
                            await repo.purge_test_run(req["purge"])
                    result = None
                elif "expire_approval" in req:
                    from sqlalchemy import text

                    async with sessions.begin() as session:
                        result = await session.execute(text(
                            "UPDATE workbench_interactions SET expires_at=now()-interval '1 second' WHERE id=:id"
                        ), {"id": req["expire_approval"]})
                        assert result.rowcount == 1
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


def configure_lab(sessions, runtime, subjects):
    from app.application.services.formal_methods import FormalMethodService
    from app.application.services.knowbot_incubation import KnowbotIncubationService
    from app.interfaces.endpoints import knowbot_routes as routes
    from app.interfaces.http.middleware import auth
    from tests.test_auth_routes_security import FakeAuthService, session as login
    from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
    from app.main import app
    from tests.knowbot_fakes import FakeRuntime

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
    accounts = {}
    for subject in subjects:
        user = login("web", "profile:read")
        accounts[subject] = user.model_copy(
            update={"principal": user.principal.model_copy(update={"subject": subject})}
        )
    auth.web_auth_service = FakeAuthService(accounts)
    routes.runtime_clients = lambda: runtime
    app.dependency_overrides.update(
        {routes.get_db_session: sql, routes.formal_service: methods}
    )


async def author(peer, template):
    import httpx
    import uvicorn
    from sqlalchemy import text
    from app.application.services.knowbot_service import KnowbotCreationService
    from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
    from app.domain.knowbots.drafts import KnowbotRequestIn
    from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
    from app.infrastructure.external.knowbot_clients import RuntimeTestClients
    from app.main import app
    from tests.knowbot_fakes import FakeRuntime, request_body
    from tests.test_knowbot_clients import FakeOidc, KNOWBENCH
    from tests.test_knowbot_repository_db import db
    from tests.test_knowbot_workdraft_routes import WEB as HEADERS, WEB_SID

    lock = asyncio.Lock()

    async def rpc(message):
        async with lock:
            peer.stdin.write((json.dumps(message) + "\n").encode())
            await peer.stdin.drain()
            return json.loads(await asyncio.wait_for(peer.stdout.readline(), 30))

    review_requests = {}
    submitted_runs = set()

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
            payload = json.loads(request.content)
            submitted_runs.add(payload["run_id"])
            graph = payload["draft"]["definition"]["procedure"]
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

        configure_lab(sessions, runtime, ["author"])
        registered_script = template["draft"]["source"]["kind"] == "registered_script"
        expected_receipt = "sandbox-provisioner" if registered_script else provisioner_revision()
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

            internal_request = await new_request("P1 internal producer replacement")
            strict_request = await new_request("P1 input with no predecessor")
            reselect_request = await new_request("P1 replacement expert")
            invalid_request = await new_request("P1 invalid fixed parameter")
            leaf_request = await new_request("P1 provider")
            expert_request = await new_request("P1 expert")
            draft = template["draft"]
            declaration = draft["definition"]["capability_declaration"]
            declaration.update(
                title="Verify provisioner revision",
                purpose="Resolve and verify a pinned image build source",
            )
            if registered_script:
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app), base_url="http://testserver",
                    headers=HEADERS, cookies={WEB_SID: "author"},
                ) as client:
                    response = await client.get(f"/api/web/v1/knowbot-requests/{leaf_request}/formal-method-sources")
                    response.raise_for_status()
                    assert draft["source"] in response.json()["items"]
            else:
                draft["definition"]["access_requirements"][0]["resources"][0]["values"] = [
                    "sandbox-provisioner",
                    provisioner_revision(),
                ]
            for side in ("inputs", "outputs"):
                for slot in draft["definition"]["procedure"][side].values():
                    slot["meaning"] = {"unit": "image-build-reference"}
                    slot["schema"]["minLength"] = 1
            await KnowbotWorkdraftService(repo).save(
                "author", leaf_request, revision=0, edits=[("formal_method", draft)]
            )
            strict = copy.deepcopy(draft)
            strict["definition"]["capability_declaration"]["title"] = (
                "Verify a deployment ticket"
            )
            strict["definition"]["procedure"]["inputs"]["to"]["meaning"] = {
                "unit": "deployment-ticket"
            }
            await KnowbotWorkdraftService(repo).save(
                "author", strict_request, revision=0, edits=[("formal_method", strict)]
            )
            if registered_script:
                join_request = await new_request("P2 concatenate two branch results")
                p2_request = await new_request("P2 expert")
                reviewer_request = await new_request("Compare an assessment with a checked output")
                staged_request = await new_request("Strict review draft")
                join = copy.deepcopy(draft)
                join["source"] = template["join_source"]
                join["definition"]["access_requirements"][0]["data_transfer"]["argument_fields"] = ["to", "other"]
                procedure = join["definition"]["procedure"]
                for field in ("kind", "source", "entry", "version", "digest"):
                    procedure["implementation"][field] = join["source"][field]
                procedure["inputs"]["other"] = copy.deepcopy(procedure["inputs"]["to"])
                procedure["outputs"]["assessment"] = copy.deepcopy(procedure["outputs"]["receipt"])
                procedure["outputs"]["assessment"]["meaning"] = {"unit": "author-assessment"}
                join["definition"]["capability_declaration"]["title"] = "Combine both verified references"
                await KnowbotWorkdraftService(repo).save(
                    "author", join_request, revision=0, edits=[("formal_method", join)]
                )
                reviewer = copy.deepcopy(join)
                reviewer["definition"]["procedure"]["inputs"]["other"]["meaning"] = {"unit": "author-assessment"}
                await KnowbotWorkdraftService(repo).save(
                    "author", reviewer_request, revision=0, edits=[("formal_method", reviewer)]
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

            async def trial(
                mid, request_id, steps, cancel=False, *,
                input_alias="to", expert_graph=False, revision=1, promise_cases=(),
                version=1, input_values=None, expected_output=None, expire_second=False,
            ):
                spec = copy.deepcopy(template["execution"])
                spec["suite"].pop("digest")
                spec["suite"]["suite_id"] = str(uuid4())
                spec["suite"]["cases"][0]["input"]["values"] = (
                    {input_alias: "sandbox-provisioner"} if input_alias is not None else {}
                )
                spec["suite"]["cases"][0]["expected"]["assertions"][0]["value"] = expected_receipt
                if input_values is not None:
                    spec["suite"]["cases"][0]["input"]["values"] = input_values
                    spec["suite"]["cases"][0]["expected"]["assertions"][0]["value"] = expected_output
                if promise_cases:
                    case = spec["suite"]["cases"][0]
                    spec["suite"]["cases"] = [
                        {**case, "case_id": name, "covers_promises": [name], "input": {"values": {input_alias: value}}}
                        for name, value in promise_cases
                    ]
                run = str(uuid4())
                command = {"request_id": request_id, "revision": revision, "run_id": run}
                prefix = f"method-units/{mid}/executions"
                await call("POST", prefix, json={**command, "execution": spec})
                endpoint = f"{prefix}/{run}"
                decisions = 0
                for _ in range(18):
                    await rpc({"advance": run})
                    result = await call(
                        "GET", endpoint, params={"request_id": request_id}
                    )
                    if expire_second and result["status"] == "failed":
                        assert decisions == 2 and not result["admission"]["receipt"]
                        evidence = await rpc({"evidence": run})
                        observed = {r["slot"]: r for r in evidence["steps"]}
                        assert set(observed) == {"branch", "branch_1"}
                        assert observed["branch"]["output_artifacts"]
                        assert not observed["branch_1"]["output_artifacts"]
                        assert result["cases"][0]["outcome"] == "rejected"
                        case = result["cases"][0]
                        report = case["partial"]
                        assert {s["step"]: s["state"] for s in report["steps"]} == {
                            "branch": "accepted", "branch_1": "failed", "step_1": "not_run",
                        }, report
                        assert report["missing_promises"]["sent"]["missing_outputs"] == ["receipt"] and not report["received"]
                        body = {"request_id": request_id, "case_id": case["case_id"],
                                "repetition": case["repetition"], "step": "branch",
                                "scope_digest": report["scope_digest"]}
                        route = endpoint + "/step-deliveries"
                        for change, expected in [
                            ({"scope_digest": "sha256:" + "0" * 64}, 409),
                            ({"step": "branch_1"}, 400), ({"step": "step_1"}, 400),
                            ({"repetition": 2}, 409),
                        ]:
                            denied = await client.post("/api/web/v1/" + route, json={**body, **change})
                            assert denied.status_code == expected, denied.text
                        review_route = endpoint + "/branch-review"
                        artifact = next(s["artifact"] for s in report["steps"] if s["step"] == "branch")
                        def review_command(expected, previous=None):
                            return {**body, "artifact": artifact, "previous": previous,
                                    "criteria": {"outputs": ["receipt"], "reviewer": "isolated_reviewer",
                                                 "assertions": [{"kind": "equals", "pointer": "/receipt", "value": expected}]}}
                        async def refused_review(command, status):
                            response = await client.post("/api/web/v1/" + review_route, json=command)
                            assert response.status_code == status, response.text
                        await refused_review(review_command("left"), 409)
                        concurrent = await rpc({"receive_concurrently": run, "body": body})
                        first = await call("POST", route, json=body)
                        assert first == {"contract_version": 1, **concurrent}
                        assert first["outputs"] == {"receipt": "left"}
                        await rpc({"purge": run})
                        assert await call("POST", route, json=body) == first
                        await refused_review({**review_command("left"), "artifact": {**artifact, "version": artifact["version"] + 1}}, 409)
                        counters = await rpc({"review_counters": True})
                        assert await rpc({"review_as_other": run, "body": review_command("left")}) == 404
                        failed = await call("POST", review_route, json=review_command("right"))
                        assert failed["review"]["status"] == "v0_failed" and not failed["review"]["handoff"]
                        assert not failed["review"]["checks"][0]["passed"]
                        await refused_review(review_command("left"), 409)
                        command = review_command("left", failed["review"]["digest"])
                        prepared = await call("POST", review_route, json=command)
                        review = prepared["review"]
                        assert review["status"] == "awaiting_isolation" and review["checks"][0]["passed"]
                        assert list(review["handoff"]) == ["receipt"] and review["digest"] != failed["review"]["digest"]
                        assert await call("POST", review_route, json=command) == prepared
                        assert await call("POST", route, json=body) == prepared
                        assert await rpc({"review_counters": True}) == counters
                        stored = await call("GET", endpoint, params={"request_id": request_id})
                        assert stored["cases"][0]["partial"]["received"] == ["branch"]
                        assert stored["status"] == "failed" and not stored["admission"]["receipt"]
                        return
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
                        if expire_second and decisions == 1:
                            await rpc({"expire_approval": action["interaction_id"]})
                            decisions += 1
                            continue
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
                assert not expire_second, "An expired required branch must stop the join"
                assert decisions == steps * len(spec["suite"]["cases"]) and result["status"] == "passed", result
                frozen = await call(
                    "PUT",
                    f"method-units/{mid}/formal-versions/{version}",
                    json={**command, "visibility": "private"},
                )
                assert frozen["definition"]["procedure"]["kind"] == (
                    "orchestration" if expert_graph or steps > 1 else "direct"
                )
                if steps > 1:
                    evidence = await rpc({"evidence": run})
                    chain = frozen["definition"]["procedure"]["steps"]
                    results = evidence["steps"]
                    assert evidence["validated"] and len(results) == len(chain) == steps
                    assert len({r["artifact"]["id"] for r in results}) == steps
                    if input_alias is None:
                        assert chain[0]["inputs"]["to"]["binding"] == {
                            "source": "literal", "value": "sandbox-provisioner",
                        }
                        expected = hashlib.sha256(b'{"to":"sandbox-provisioner"}').hexdigest()
                        assert results[0]["inputs_digest"] == expected
                    if registered_script and mid == p2_id:
                        case = result["cases"][0]
                        report = case["verified_steps"]
                        assert "partial" not in case and not report["missing_promises"]
                        step = next(s for s in report["steps"] if s["step"] == chain[-1]["id"])
                        selected = {"request_id": request_id, "case_id": case["case_id"], "repetition": case["repetition"],
                                    "step": step["step"], "scope_digest": report["scope_digest"]}
                        receipt = await call("POST", endpoint + "/step-deliveries", json=selected)
                        assert receipt["outputs"] == results[-1]["outputs"]
                        command = {**selected, "artifact": step["artifact"], "previous": None, "criteria": {
                            "outputs": ["receipt"], "reviewer": "different_model_family",
                            "comparison": {"assessment_output": "assessment", "max_reworks": 2},
                            "assertions": [{"kind": "equals", "pointer": "/receipt", "value": expected_output or expected_receipt}]}}
                        counters = await rpc({"review_counters": True})
                        prepared = await call("POST", endpoint + "/branch-review", json=command)
                        review = prepared["review"]
                        assert review["status"] == "awaiting_isolation" and prepared["artifact"] == step["artifact"]
                        assert set(review["handoff"]) == {"receipt"}
                        assert review["deferred"] == {"assessment_output": "assessment",
                            "assessment_digest": "sha256:" + hashlib.sha256(json.dumps(receipt["outputs"]["assessment"]).encode()).hexdigest(),
                            "opens_after": "independent_findings_sealed", "unresolved_to": "task_owner"}
                        assert await call("POST", endpoint + "/step-deliveries", json=selected) == prepared
                        assert await rpc({"review_counters": True}) == counters
                    by_step = {row["slot"]: row for row in results}
                    for node in chain:
                        expected_inputs = {
                            entry["binding"]["step"] for entry in node["inputs"].values()
                            if entry["binding"]["source"] == "step"
                        }
                        actual = by_step[node["id"]]["input_bindings"]
                        assert len(actual) == len(expected_inputs)
                        for producer in expected_inputs:
                            assert {"step_id": producer, **by_step[producer]["artifact"]} in actual
                    assert results[-1]["outputs"]["receipt"] == (expected_output or expected_receipt)
                return frozen

            leaf_id, expert_id = str(uuid4()), str(uuid4())
            leaf = await trial(leaf_id, leaf_request, 1)
            strict_id, reselect_id, internal_id = str(uuid4()), str(uuid4()), str(uuid4())
            await trial(strict_id, strict_request, 1)
            extra_env = {}
            if registered_script:
                join_id, p2_id = str(uuid4()), str(uuid4())
                await trial(
                    join_id, join_request, 1, input_values={"to": "left", "other": "right"},
                    expected_output="left|right",
                )
                extra_env = {"LUNA_P2_REQUEST": p2_request, "LUNA_P2_METHOD": p2_id, "LUNA_P2_JOIN": join_id}
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
                    from p1_sample_peer import author_sample

                    async with author_sample(app, sessions):
                        child = await asyncio.create_subprocess_exec(
                            "pnpm",
                            "exec",
                            "vitest",
                            "run",
                            "tests/component/p1-live.test.tsx",
                            cwd=WEB,
                            env={
                                **os.environ,
                                **extra_env,
                                "LUNA_P1_URL": url,
                                "LUNA_P1_SAMPLE": "1",
                                "LUNA_P1_INTERNAL_REQUEST": internal_request,
                                "LUNA_P1_INTERNAL_METHOD": internal_id,
                                "LUNA_P1_REQUEST": expert_request,
                                "LUNA_P1_METHOD": expert_id,
                                "LUNA_P1_STRICT": strict_id,
                                "LUNA_P1_RESELECT_REQUEST": reselect_request,
                                "LUNA_P1_RESELECT_METHOD": reselect_id,
                                "LUNA_P1_LEAF": leaf_id,
                            },
                        )
                        assert await child.wait() == 0, "author component failed"
                finally:
                    server.should_exit = True
                    await serving
            if registered_script:
                two_inputs = {"branch_to": "left", "branch_1_to": "right"}
                await trial(
                    p2_id, p2_request, 3, input_values=two_inputs,
                    expected_output="left|right", expire_second=True,
                )
                p2 = await trial(p2_id, p2_request, 3, input_values=two_inputs, expected_output="left|right")
                left, right, merge = p2["definition"]["procedure"]["steps"]
                assert not left["depends_on"] and not right["depends_on"]
                assert merge["depends_on"] == [left["id"], right["id"]]
                # Use actual frozen contracts on both sides of the saved review edge.
                reviewer_id = str(uuid4())
                frozen_reviewer = await trial(reviewer_id, reviewer_request, 1,
                    input_values={"to": "left", "other": "right"}, expected_output="left|right")
                document = (await call("GET", f"knowbot-requests/{p2_request}/workdraft"))["body"]["formal_method"]
                graph = document["definition"]["procedure"]
                target = copy.deepcopy(merge)
                target.update(id="review", depends_on=[merge["id"]], candidates=[{
                    "method_id": reviewer_id, "version": 1, "digest": frozen_reviewer["digest"]}])
                for param, output in (("to", "receipt"), ("other", "assessment")):
                    target["inputs"][param] = {"slot": reviewer["definition"]["procedure"]["inputs"][param],
                        "binding": {"source": "step", "step": merge["id"], "output": output}}
                graph["steps"].append(target)
                graph["max_steps"] = graph["max_expansions"] = 10
                for export in graph["exports"].values():
                    export["step"] = "review"
                roles = {"review": {"review_requirements": {merge["id"]: "isolated_reviewer"},
                    "comparison": {"assessment_output": "assessment", "max_reworks": 1}}}
                review_path = f"knowbot-requests/{staged_request}/workdraft"
                await call("POST", review_path + "/cells", json={"revision": 0, "cells": [
                    {"path": "formal_method", "value": document}, {"path": "collaboration", "value": roles}]})
                reopened = await call("GET", review_path)
                assert reopened["body"]["collaboration"]["review"]["comparison"] == roles["review"]["comparison"]
                assert {"step": "review", "primitive": "sealed_findings"} in reopened["runtime_gaps"]
                spec = copy.deepcopy(template["execution"])
                spec["suite"].pop("digest")
                spec["suite"]["suite_id"] = str(uuid4())
                spec["suite"]["cases"][0]["input"]["values"] = two_inputs
                command = {"request_id": staged_request, "run_id": str(uuid4()), "revision": 1, "execution": spec}
                counters = await rpc({"review_counters": True})
                response = await client.post(f"/api/web/v1/method-units/{uuid4()}/executions", json=command)
                assert response.status_code == 409 and response.json()["code"] == "runtime_capability_gap", response.text
                assert review_requests["formal-method-executions"] == reopened["body"]["collaboration"]
                assert await rpc({"review_counters": True}) == counters
                print("P3 verified: strict draft reopened, author assessment withheld, execution blocked before dispatch")
                print(
                    "P2 verified: scoped lookup, adoption, reopen, expired second approval, "
                    "partial scope receipt after cleanup, completed and partial V0 review drafts, both branch artifacts and private freeze", p2["digest"],
                )
            internal = await trial(
                internal_id, internal_request, 2, revision=2, input_alias="buildSource"
            )
            internal_graph = internal["definition"]["procedure"]
            assert [
                node["candidates"][0]["method_id"] for node in internal_graph["steps"]
            ] == [leaf_id, leaf_id]
            assert internal_graph["exports"]["receipt"]["step"] == "step_1"
            replaced = await trial(
                reselect_id,
                reselect_request,
                1,
                input_alias="buildSource",
                expert_graph=True,
            )
            graph = replaced["definition"]["procedure"]
            assert graph["steps"][0]["candidates"] == [
                {"method_id": leaf_id, "version": 1, "digest": leaf["digest"]}
            ]
            assert graph["steps"][0]["inputs"]["to"]["binding"] == {
                "source": "caller",
                "name": "buildSource",
            }
            assert graph["exports"]["receipt"]["output"] == "receipt"
            for field in ("capability_declaration", "how_to_validate"):
                assert replaced["definition"][field] == strict["definition"][field]
            if not registered_script:
                path = f"knowbot-requests/{reselect_request}/workdraft"
                current = await call("GET", path)
                candidate = current["body"]["formal_method"]
                definition = candidate["definition"]
                declaration = definition["capability_declaration"]
                named = next(iter(declaration["promises"]))
                declaration["promises"][named] = "Resolve a component name to its build revision"
                declaration["promises"]["pinned"] = "Verify a supplied revision against the manifest"
                declaration["conditions"] = {
                    named: {"when": "A component name is supplied", "input_slots": ["buildSource"]},
                    "pinned": {"when": "A revision is supplied", "input_slots": ["buildSource"]},
                }
                definition["how_to_validate"].append({**definition["how_to_validate"][0], "promise_id": "pinned"})
                updated = await call("POST", path + "/cells", json={
                    "revision": current["revision"], "cells": [{"path": "formal_method", "value": candidate}],
                })
                checked = await trial(reselect_id, reselect_request, 1, input_alias="buildSource",
                    expert_graph=True, revision=updated["revision"], version=2,
                    promise_cases=[(named, "sandbox-provisioner"), ("pinned", expected_receipt)])
                assert checked["definition"] == definition and checked["digest"] != replaced["digest"]
                old = await call("GET", f"method-units/{reselect_id}/formal-versions/1")
                assert old["definition"] == replaced["definition"] and old["digest"] == replaced["digest"]
            await trial(expert_id, expert_request, 3, cancel=True, input_alias=None, revision=3)
            expert = await trial(expert_id, expert_request, 3, input_alias=None, revision=3)
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
            invalid = (await call("GET", path))["body"]["formal_method"]
            invalid["definition"]["procedure"]["steps"][0]["inputs"]["to"]["binding"]["value"] = ""
            await call(
                "POST", f"knowbot-requests/{invalid_request}/workdraft/cells",
                json={"revision": 0, "cells": [{"path": "formal_method", "value": invalid}]},
            )
            invalid_run = str(uuid4())
            bad = await client.post(
                f"/api/web/v1/method-units/{uuid4()}/validations",
                json={"request_id": invalid_request, "revision": 1, "run_id": invalid_run},
            )
            assert bad.status_code == 400 and bad.json()["code"] == "formal_method_invalid", bad.text
            assert "Fixed input" in bad.json()["detail"] and invalid_run not in submitted_runs
            saved = await call(
                "POST",
                path + "/cells",
                json={
                    "revision": 3,
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
            assert saved["revision"] == 4
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
                    "revision": 4,
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
                    "revision": 4,
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
                "P1 verified: sample header, bounded lookup, internal and downstream "
                "replacement, reopened plans, cancellation, artifacts and freeze",
                expert["digest"],
            )
    finally:
        await schema.aclose()


async def main():
    peer = await asyncio.create_subprocess_exec(
        str(BENCH / ".venv/bin/python"),
        __file__,
        "--bench",
        *sys.argv[1:],
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
    provider = "--bench" in sys.argv[1:]
    root = BENCH if provider else LAB
    sys.path[:0] = [str(root), str(root / "tests")]
    asyncio.run(bench("--registered-script" in sys.argv[1:]) if provider else main())
