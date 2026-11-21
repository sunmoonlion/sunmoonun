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
    from fastapi import Header
    from test_instruction_runner_db import stack
    from test_instruction_requests_db import PRICES, ROUTE
    from test_workbench_ledger_db import db
    from app.application.workbench.formal_methods import FormalMethods
    from app.application.workbench.formal_test_runs import FormalExecutions
    from app.application.workbench.instruction_requests import InstructionRequests
    from app.application.workbench.test_runs import KnowbotTestConductor
    from app.bootstrap.api import create_app
    from app.bootstrap.workbench import workbench_stores
    from app.infrastructure.workbench.repository import WorkbenchRepository
    from app.interfaces.endpoints import knowbot_runtime_routes as routes
    from core.config import Settings

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

        def factory(repo):
            return SimpleNamespace(
                formal_sources=FormalMethods(repo, source_licenses=(license,))
            )

        route = partial(
            InstructionRequests.for_account,
            routes=(ROUTE,),
            model=ROUTE.model,
            prices=PRICES,
            default_url=ROUTE.base_url,
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
    from tests.test_knowbot_clients import FakeOidc, KNOWBENCH
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
            dict(
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                content=request.content.decode(),
            )
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

            command = dict(request_id=str(req.id), run_id=str(uuid4()), revision=1)
            spec = dict(
                suite=dict(
                    suite_id=str(uuid4()),
                    version=1,
                    cases=[
                        dict(
                            case_id="summary",
                            input={"values": {"status": "ready"}},
                            repetitions=1,
                            minimum_passes=1,
                            expected={
                                "outcome": "succeeded",
                                "assertions": [
                                    {
                                        "kind": "equals",
                                        "pointer": "/summary",
                                        "value": "ready",
                                    }
                                ],
                            },
                        )
                    ],
                ),
                runner=dict(
                    kind="user", environment_id=env, workspace_root="/home/u/research"
                ),
                budget={"limit": "1", "currency": "CNY"},
                timeout_seconds=120,
                max_wait_seconds=120,
            )
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
            print(
                "Author instruction trial passed and registered private v1:",
                frozen["digest"],
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
