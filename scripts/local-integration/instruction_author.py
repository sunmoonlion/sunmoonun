"""Run from the worktree using KnowLab's venv and the two disposable *_tests DB URLs.

Exercise the author API, runtime client, KnowBench API/conductor, worker and version
registration. Account, computer, worker transport and provider use synthetic fixtures.
"""

import asyncio
import json
import sys
from functools import partial
from types import SimpleNamespace
from uuid import uuid4

from p1_author import BENCH, LAB, configure_lab


async def bench():
    import httpx
    from app.application.workbench.capabilities import Capabilities
    from app.application.workbench.formal_test_runs import FormalExecutions
    from app.application.workbench.instruction_requests import InstructionRequests
    from app.application.workbench.test_runs import KnowbotTestConductor
    from app.bootstrap.api import create_app
    from app.bootstrap.workbench import workbench_stores
    from app.infrastructure.workbench.repository import WorkbenchRepository
    from app.interfaces.endpoints import knowbot_runtime_routes as routes
    from core.config import Settings
    from fastapi import Header
    from test_capabilities_db import Remote
    from test_instruction_requests_db import PRICES, ROUTE
    from test_instruction_runner_db import stack
    from test_workbench_ledger_db import db

    schema = db.__wrapped__()
    sessions = await anext(schema)
    prepared, task_id = (asyncio.get_running_loop().create_future() for _ in range(2))

    async def prepare(db, req, license, env):
        prepared.set_result((req.draft, license, env))
        return await task_id

    worker = asyncio.create_task(stack(sessions, author_trial=prepare))
    try:
        done, _ = await asyncio.wait(
            (prepared, worker), return_when=asyncio.FIRST_COMPLETED
        )
        if worker in done:
            await worker
        draft, license, environment = prepared.result()

        route = partial(
            InstructionRequests.for_account,
            routes=(ROUTE,),
            model=ROUTE.model,
            prices=PRICES,
            default_url=ROUTE.base_url,
        )

        def factory(repo):
            return Capabilities(
                repo, Remote(), source_licenses=(license,), instruction_service=route
            )

        async def executions():
            async with sessions() as session:
                repo = WorkbenchRepository(session)
                yield FormalExecutions(repo, factory(repo), instruction_service=route)

        async def methods():
            async for service in executions():
                yield service.formal

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
        conductor = KnowbotTestConductor(
            workbench_stores(sessions), formal_capabilities=factory
        )
        print(
            json.dumps([draft.model_dump(mode="json", by_alias=True), environment]),
            flush=True,
        )
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) as client:
            for line in sys.stdin:
                message = json.loads(line)
                if "run" in message:
                    run = message["run"]
                    await conductor.advance(run)
                    async with sessions() as session:
                        (case,) = await WorkbenchRepository(session).list_test_cases(
                            run
                        )
                    task_id.set_result(str(case["task_id"]))
                    runner = await worker
                    runner.units.ready = True
                    assert await runner.runner.run_once() >= 1
                    if active := runner.runner.driving.get(runner.task):
                        await active
                    if runner.runner.instruction_cleanup:
                        await runner.runner.instruction_cleanup
                    for _ in range(3):
                        await conductor.advance(run)
                    assert len(runner.turns) == 1
                    reply = True
                elif "advance" in message:
                    run = message["advance"]
                    await conductor.advance(run)
                    async with sessions() as session:
                        repo = WorkbenchRepository(session)
                        (case,) = await repo.list_test_cases(run)
                        task = await repo.get_task(str(case["task_id"]))
                    if task["state"] == "RUNNING":
                        fixture = await worker
                        fixture.units.task = str(task["id"])
                        fixture.units.uid, fixture.units.worker = (
                            str(uuid4()),
                            str(uuid4()),
                        )
                        async with fixture.host() as svc, svc.repo.transaction():
                            _, job = await svc.authority(
                                str(task["owner_actor_id"]), task, "knowlab"
                            )
                        fixture.wire["input"][0]["content"][0]["text"] = json.dumps(
                            job["input"]
                        )
                        fixture.runner.capabilities = factory
                        await fixture.runner.handle(
                            {
                                "kind": "task.drive",
                                "session_id": str(task["session_id"]),
                                "payload": {"task_id": str(task["id"])},
                            }
                        )
                        await fixture.runner.driving[str(task["id"])]
                    reply = True
                else:
                    response = await client.request(**message)
                    reply = [response.status_code, response.text]
                print(json.dumps(reply), flush=True)
    finally:
        worker.cancel()
        await asyncio.gather(worker, return_exceptions=True)
        await schema.aclose()


async def author(peer):
    import httpx
    from app.application.services.knowbot_service import KnowbotCreationService
    from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
    from app.domain.knowbots.drafts import KnowbotRequestIn
    from app.infrastructure.external.knowbot_clients import RuntimeTestClients
    from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
    from app.main import app
    from tests.knowbot_fakes import FakeRuntime, request_body
    from tests.test_knowbot_clients import KNOWBENCH, FakeOidc
    from tests.test_knowbot_repository_db import db
    from tests.test_knowbot_workdraft_routes import WEB, WEB_SID

    async def read():
        return json.loads(await asyncio.wait_for(peer.stdout.readline(), 45))

    async def rpc(message):
        peer.stdin.write((json.dumps(message) + "\n").encode())
        await peer.stdin.drain()
        return await read()

    async def forward(request):
        code, body = await rpc(
            {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "content": request.content.decode(),
            }
        )
        return httpx.Response(code, content=body)

    draft, env = await read()
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
        async with sessions() as session:
            repo = SqlKnowlabRepository(session)
            req = await KnowbotCreationService(repo, FakeRuntime()).submit(
                "author", KnowbotRequestIn.model_validate(request_body())
            )
            await KnowbotWorkdraftService(repo).save(
                "author", str(req.id), revision=0, edits=[("formal_method", draft)]
            )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            headers=WEB,
            cookies={WEB_SID: "author"},
        ) as client:
            prefix = "/api/web/v1/method-units/" + str(uuid4())

            async def call(method, path, **kwargs):
                response = await client.request(method, prefix + path, **kwargs)
                assert response.is_success, (response.status_code, response.text)
                return response.json()

            command = {"request_id": str(req.id), "run_id": str(uuid4()), "revision": 1}
            spec = {
                "suite": {
                    "suite_id": str(uuid4()),
                    "version": 1,
                    "cases": [
                        {
                            "case_id": "summary",
                            "input": {"values": {"status": "ready"}},
                            "repetitions": 1,
                            "minimum_passes": 1,
                            "expected": {
                                "outcome": "succeeded",
                                "assertions": [
                                    {
                                        "kind": "equals",
                                        "pointer": "/summary",
                                        "value": "ready",
                                    }
                                ],
                            },
                        }
                    ],
                },
                "runner": {
                    "kind": "user",
                    "environment_id": env,
                    "workspace_root": "/home/u/research",
                },
                "budget": {"limit": "1", "currency": "CNY"},
                "timeout_seconds": 120,
                "max_wait_seconds": 120,
            }
            assert (
                await call("POST", "/executions", json={**command, "execution": spec})
            )["status"] == "pending"
            assert await rpc({"run": command["run_id"]})
            result = await call(
                "GET",
                "/executions/" + command["run_id"],
                params={"request_id": str(req.id)},
            )
            assert (
                result["status"] == "passed"
                and result["cases"][0]["assertions"][0]["passed"]
            ), result
            denied = await client.put(
                prefix + "/formal-versions/1", json={**command, "visibility": "public"}
            )
            assert (
                denied.status_code == 400
                and denied.json()["code"] == "formal_instruction_trial_required"
            ), denied.text
            frozen = await call(
                "PUT", "/formal-versions/1", json={**command, "visibility": "private"}
            )
            assert frozen["provenance"]["validation"] == result["admission"]["receipt"]
            again = await call(
                "PUT", "/formal-versions/1", json={**command, "visibility": "private"}
            )
            assert frozen["digest"] == again["digest"]
            leaf_ref = {
                "method_id": prefix.rsplit("/", 1)[1],
                "version": 1,
                "digest": frozen["digest"],
            }
            definition = draft["definition"]
            procedure = definition["procedure"]
            steps = []
            for name, binding, deps in (
                ("first", {"source": "caller", "name": "status"}, []),
                (
                    "second",
                    {"source": "step", "step": "first", "output": "summary"},
                    ["first"],
                ),
            ):
                steps.append(
                    {
                        "id": name,
                        "candidates": [leaf_ref],
                        "select_when": "Only candidate",
                        "required_when": "Always",
                        "always_required": True,
                        "depends_on": deps,
                        "inputs": {
                            "status": {
                                "slot": procedure["inputs"]["status"],
                                "binding": binding,
                            }
                        },
                        "outputs": procedure["outputs"],
                        "on_failure": "fail",
                    }
                )
            definition["procedure"] = {
                "kind": "orchestration",
                "instructions": "Review then summarize",
                "steps": steps,
                "exports": {
                    "summary": {
                        "step": "second",
                        "output": "summary",
                        "always_present": True,
                    }
                },
                "max_depth": 2,
                "max_expansions": 3,
                "max_steps": 2,
                "max_replans": 0,
            }
            candidate = leaf_ref
            digests = [frozen["digest"]]
            for depth, leaf_count in ((2, 2), (3, 4)):
                for step in steps:
                    step["candidates"] = [candidate]
                definition["procedure"].update(
                    max_depth=depth,
                    max_steps=2 if depth == 2 else 6,
                    max_expansions=3 if depth == 2 else 7,
                )
                async with sessions() as session:
                    repo = SqlKnowlabRepository(session)
                    expert = await KnowbotCreationService(repo, FakeRuntime()).submit(
                        "author",
                        KnowbotRequestIn.model_validate(
                            request_body(title=f"Instruction expert at depth {depth}")
                        ),
                    )
                    await KnowbotWorkdraftService(repo).save(
                        "author",
                        str(expert.id),
                        revision=0,
                        edits=[
                            (
                                "formal_method",
                                {
                                    "definition": definition,
                                    "source": None,
                                    "allowed_callers": ["host"],
                                },
                            )
                        ],
                    )
                prefix = "/api/web/v1/method-units/" + str(uuid4())
                command = {
                    "request_id": str(expert.id),
                    "run_id": str(uuid4()),
                    "revision": 1,
                }
                spec["suite"]["suite_id"] = str(uuid4())
                spec["suite"]["cases"][0]["input"]["values"]["status"] = (
                    "awaiting review"
                )
                await call("POST", "/executions", json={**command, "execution": spec})
                endpoint = "/executions/" + command["run_id"]
                approvals = []
                for _ in range(12):
                    await rpc({"advance": command["run_id"]})
                    result = await call(
                        "GET", endpoint, params={"request_id": str(expert.id)}
                    )
                    if result["status"] == "passed":
                        break
                    assert result["status"] in ("pending", "running", "waiting"), result
                    for action in result["actions"]:
                        subject = action["subject"]
                        approvals.append(subject["arguments"]["status"])
                        if depth == 2 and len(approvals) == 2:
                            bound = subject["artifact_read"]["fields"]["status"]
                            assert (
                                bound["name"] == "formal-step:first"
                                and bound["version"] == 1
                                and bound["output"] == "summary"
                            )
                        if depth == 3:
                            binding = subject["artifact_read"]
                            assert len(binding["path"]) == 3
                            if len(approvals) == 3:
                                assert binding["fields"]["status"]["producer_path"] == [
                                    "first"
                                ]
                        await call(
                            "POST",
                            endpoint + "/actions/" + action["call_id"],
                            json={
                                **{
                                    k: action[k]
                                    for k in (
                                        "case_id",
                                        "repetition",
                                        "token",
                                        "subject_digest",
                                    )
                                },
                                "request_id": str(expert.id),
                                "decision": "accept",
                            },
                        )
                assert result["status"] == "passed" and approvals == [
                    "awaiting review"
                ] + ["ready"] * (leaf_count - 1), result
                frozen_expert = await call(
                    "PUT",
                    "/formal-versions/1",
                    json={**command, "visibility": "private"},
                )
                assert (
                    frozen_expert["provenance"]["validation"]
                    == result["admission"]["receipt"]
                )
                candidate = {
                    "method_id": prefix.rsplit("/", 1)[1],
                    "version": 1,
                    "digest": frozen_expert["digest"],
                }
                digests.append(candidate["digest"])
            print(
                "Registered private instruction, two-leaf expert and four-leaf nested expert:",
                *digests,
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
    )
    try:
        await author(peer)
    finally:
        peer.stdin.close()
        try:
            await asyncio.wait_for(peer.wait(), 30)
        except TimeoutError:
            peer.kill()
            await peer.wait()
            raise


if __name__ == "__main__":
    provider = sys.argv[1:] == ["--bench"]
    root = BENCH if provider else LAB
    sys.path[:0] = [str(root), str(root / "tests")]
    asyncio.run(bench() if provider else main())
