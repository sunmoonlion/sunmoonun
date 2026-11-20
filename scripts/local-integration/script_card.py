"""Drive the real script approval card against local PostgreSQL and a KIND provisioner.

Run with the KnowBench backend venv after building the matching Next frontend.
Set AGENT_TEST_DATABASE_URL, SCRIPT_TEST_PROVISIONER_URL and SCRIPT_TEST_PROVISIONER_TOKEN.
Browser login and the originating Codex events are synthetic.
"""

import asyncio
import base64
import io
import os
import socket
import sys
import zipfile
from contextlib import AsyncExitStack, closing
from pathlib import Path
from urllib.parse import urlsplit

WORKSPACE = Path(__file__).resolve().parents[3]
BACKEND = WORKSPACE / "knowbench-app/knowbench-backend/app"
WEB = WORKSPACE / "knowbench-app/knowbench-web-frontend/app"

SCRIPT = """import os, sys, time
from pathlib import Path
action = sys.stdin.read().strip()
if action == "stop":
    time.sleep(25)
elif action == "finish":
    (Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "answer.txt").write_bytes(b"42")
else:
    raise ValueError("unexpected test input")
"""


async def main():
    import uvicorn
    from app.application.workbench.session_service import SessionService
    from app.domain.workbench.capabilities import SelectionPut, tool_key
    from app.domain.workbench.skill_package import SkillPackageCreate
    from app.infrastructure.workbench.repository import WorkbenchRepository
    from app.infrastructure.workbench.skill_executor import SkillExecutor
    from app.interfaces.endpoints import capability_routes as routes
    from app.interfaces.http.middleware.auth import get_web_current_user
    from fastapi import FastAPI, HTTPException, Request
    from scripts import pair_fixture
    from test_capabilities_db import service
    from test_workbench_ledger_db import OWNER, db, seed
    from test_workbench_routes import principal
    from tool_invocation_support import request_call

    for key in ("AGENT_TEST_DATABASE_URL", "SCRIPT_TEST_PROVISIONER_URL"):
        endpoint = urlsplit(os.environ[key])
        if endpoint.hostname not in {"localhost", "127.0.0.1"} or (
            key.endswith("DATABASE_URL") and not endpoint.path.endswith("_tests")
        ):
            raise ValueError(f"{key} requires an isolated local test endpoint")
    executor = SkillExecutor(
        os.environ["SCRIPT_TEST_PROVISIONER_URL"],
        os.environ["SCRIPT_TEST_PROVISIONER_TOKEN"],
    )

    def capability(session):
        svc = service(WorkbenchRepository(session))
        svc.script_executor = executor
        return svc

    async with AsyncExitStack() as stack:
        database = db.__wrapped__()
        factory = await anext(database)
        stack.push_async_callback(database.aclose)
        await seed(factory)
        async with factory() as session:
            svc = capability(session)
            sid = (
                await SessionService(svc.repo).start(owner_actor_id=OWNER, kind="chat")
            )["session_id"]
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, "w") as package:
                package.writestr("SKILL.md", "Run scripts/calculate.py")
                package.writestr("scripts/calculate.py", SCRIPT)
            asset = await svc.create_skill(
                OWNER,
                SkillPackageCreate(
                    request_id="script-card-probe",
                    name="card-probe",
                    description="Local script card",
                    version="1",
                    archive_base64=base64.b64encode(archive.getvalue()).decode(),
                ),
                package=True,
            )
            selection = await svc.selection(OWNER, sid)
            await svc.save_selection(
                OWNER,
                sid,
                SelectionPut(
                    revision=selection["revision"],
                    skills=[asset["id"]],
                    purpose="Test the script approval card",
                ),
            )
            config = (await svc.prepare(OWNER, sid))["config"][
                "mcp_servers.sunmoon_capabilities"
            ]
            token = config["http_headers"]["Authorization"].split()[1]
            tool = tool_key(asset["id"], "skill_run")
            calls = {}
            for action in ("finish", "stop"):
                call = await request_call(
                    svc,
                    sid,
                    token,
                    tool,
                    {"path": "scripts/calculate.py", "stdin": action},
                    call_id=action,
                )
                assert call["status"] == "awaiting_approval"
                calls[action] = call["call_id"]
                stack.push_async_callback(executor.cancel, OWNER, call["call_id"])

        async def service_for_request():
            async with factory() as session:
                yield capability(session)

        def user(request: Request):
            if request.cookies.get("sunmoonai_knowbench_web_sid") != "e2e-session":
                raise HTTPException(401)
            if request.method == "POST" and not pair_fixture._csrf_allowed(
                request, request.headers.get("x-csrf-token")
            ):
                raise HTTPException(403)
            return principal(OWNER)

        api = FastAPI()
        api.include_router(routes.router, prefix="/api")
        api.include_router(pair_fixture.app.router)
        api.dependency_overrides[routes.service] = service_for_request
        api.dependency_overrides[get_web_current_user] = user
        api.dependency_overrides[routes.require_workbench_enabled] = lambda: None

        async def reconcile():
            while True:
                async with factory() as session:
                    await capability(session).reconcile_scripts()
                await asyncio.sleep(0.4)

        sock = stack.enter_context(closing(socket.socket()))
        sock.bind(("127.0.0.1", 0))
        sock.listen()
        with socket.socket() as gateway, socket.socket() as next_server:
            for listener in (gateway, next_server):
                listener.bind(("127.0.0.1", 0))
            gateway_port, next_port = (
                gateway.getsockname()[1],
                next_server.getsockname()[1],
            )
        pair_fixture._origin = f"http://127.0.0.1:{gateway_port}"
        server = uvicorn.Server(
            uvicorn.Config(api, access_log=False, log_level="error")
        )
        serving = asyncio.create_task(server.serve(sockets=[sock]))
        try:
            async with asyncio.timeout(10):
                while not server.started:
                    if serving.done():
                        await serving
                        raise RuntimeError("Local test API exited")
                    await asyncio.sleep(0.05)
            env = dict(
                os.environ,
                PORT=str(gateway_port),
                NEXT_PORT=str(next_port),
                PAIR_FIXTURE_PORT=str(sock.getsockname()[1]),
                SCRIPT_CARD_SESSION=sid,
                CI="",
            )
            env.pop("PLAYWRIGHT_BASE_URL", None)
            browser = await asyncio.create_subprocess_exec(
                "pnpm",
                "exec",
                "playwright",
                "test",
                "-g",
                "live isolated script card",
                "--workers=1",
                cwd=WEB,
                env=env,
            )
            runner = asyncio.create_task(reconcile())
            done = asyncio.create_task(browser.wait())
            try:
                finished, _ = await asyncio.wait(
                    (runner, done), return_when=asyncio.FIRST_COMPLETED
                )
                if runner in finished:
                    await runner
                if await done:
                    raise RuntimeError("Browser script card acceptance failed")
            finally:
                if browser.returncode is None:
                    browser.terminate()
                    await done
                runner.cancel()
                await asyncio.gather(runner, return_exceptions=True)
            async with factory() as session:
                retained = {
                    c["id"]: c for c in await capability(session).calls(OWNER, sid)
                }
                assert set(retained) == set(calls.values())
                assert retained[calls["finish"]]["status"] == "succeeded"
                stopped = retained[calls["stop"]]
                assert (
                    stopped["status"] == "failed"
                    and "stop" in str(stopped["detail"]["result"]).lower()
                )
            for call_id in calls.values():
                assert (await executor.status(OWNER, call_id))["state"] == "absent"
            print(
                "Original calls retained, downloaded 42, both Jobs released.",
                flush=True,
            )
        finally:
            server.should_exit = True
            await serving


if __name__ == "__main__":
    sys.path[:0] = [str(BACKEND), str(BACKEND / "tests")]
    asyncio.run(main())
