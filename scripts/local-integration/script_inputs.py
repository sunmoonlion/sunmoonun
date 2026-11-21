"""Run synthetic KnowBase data through an approved KnowBench call and a local test provisioner.

Each backend needs its .venv and its own local *_tests PostgreSQL database.
SCRIPT_TEST_PROVISIONER_URL and SCRIPT_TEST_PROVISIONER_TOKEN select a running test
provisioner with the matching sandbox image. The probe owns only its random actor's Job.
"""

import asyncio
import base64
import io
import json
import os
import sys
import tempfile
import zipfile
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit

SCRIPT = Path(__file__).resolve()
WORKSPACE = SCRIPT.parents[3]


async def launch(app, mode, env):
    cwd = WORKSPACE / f"{app}-app" / f"{app}-backend" / "app"
    proc = await asyncio.create_subprocess_exec(
        str(cwd / ".venv/bin/python"),
        str(SCRIPT),
        mode,
        cwd=cwd,
        env=env,
    )
    try:
        if await proc.wait():
            raise RuntimeError(f"{app} script input probe failed")
    finally:
        if proc.returncode is None:
            proc.terminate()
            await proc.wait()


async def source():
    from app.application.services.data_query_revisions import function_revision
    import uvicorn
    from test_data_mcp import KEY, PUBLIC_OWNER, World
    from test_durable_delivery_db import db

    database = db.__wrapped__()
    world = World(await anext(database))
    try:
        material, _ = await world.publish()
        processing = await world.runs.issue_processing(
            "knowfeed", PUBLIC_OWNER, material.id, 1
        )
        await world.runs.write_rendition(
            "knowfeed",
            processing.id,
            "text",
            "probe",
            b"21",
            title="Script input",
            published_on=date(2026, 1, 1),
        )
        session = await world.runs.register_session("alice", "knowbench")
        with tempfile.TemporaryDirectory() as directory:
            socket = str(Path(directory) / "source.sock")
            server = uvicorn.Server(
                uvicorn.Config(
                    world.client._transport.app,
                    uds=socket,
                    access_log=False,
                    log_level="error",
                )
            )
            serving = asyncio.create_task(server.serve())
            try:
                async with asyncio.timeout(10):
                    while not server.started:
                        if serving.done():
                            await serving
                            raise RuntimeError("KnowBase test service did not start")
                        await asyncio.sleep(0.05)
                await launch(
                    "knowbench",
                    "consume",
                    dict(
                        os.environ,
                        SCRIPT_SOURCE_SOCKET=socket,
                        SCRIPT_SOURCE_REVISION=json.dumps(
                            function_revision("read_input")
                        ),
                        SCRIPT_SOURCE_MATERIAL=str(material.id),
                        SCRIPT_SOURCE_SESSION=str(session.id),
                        SCRIPT_SYNTHETIC_KEY=KEY.as_pem(private=True).decode(),
                    ),
                )
            finally:
                server.should_exit = True
                await serving
    finally:
        await world.client.aclose()
        await database.aclose()


async def consume():
    import httpx
    from app.application.workbench.tokens import TokenIssuer
    from app.domain.workbench.capabilities import tool_key
    from app.domain.workbench.skill_package import SkillPackageCreate
    from app.infrastructure.workbench.repository import WorkbenchRepository
    from app.infrastructure.workbench.skill_executor import SkillExecutor
    from sqlalchemy import text
    from test_capabilities_db import approval, service
    from test_workbench_ledger_db import OWNER, db, seed
    from tool_invocation_support import request_call

    from app.domain.workbench.service_functions import FunctionRevision
    from app.infrastructure.workbench.service_functions import register_revision

    class Source:
        async def invoke_data_query(self, name, token, body):
            assert name == "read_input"
            transport = httpx.AsyncHTTPTransport(uds=os.environ["SCRIPT_SOURCE_SOCKET"])
            async with httpx.AsyncClient(
                transport=transport, base_url="http://localhost"
            ) as client:
                reply = await client.post(
                    f"/internal/v1/functions/{name}/1",
                    headers={"Authorization": "Bearer " + token},
                    json=body,
                )
                reply.raise_for_status()
                return reply.json()

    database = db.__wrapped__()
    factory = await anext(database)
    executor = SkillExecutor(
        os.environ["SCRIPT_TEST_PROVISIONER_URL"],
        os.environ["SCRIPT_TEST_PROVISIONER_TOKEN"],
    )
    call_id = None
    try:
        async with factory() as session:
            await register_revision(
                session,
                FunctionRevision.model_validate_json(
                    os.environ["SCRIPT_SOURCE_REVISION"]
                ),
            )
        _, _, sid = await seed(factory)
        async with factory() as session:
            repo = WorkbenchRepository(session)
            svc = service(repo)
            svc.script_executor = executor
            svc.script_material_source = (
                Source(),
                TokenIssuer(os.environ["SCRIPT_SYNTHETIC_KEY"], issuer="knowbench"),
            )
            async with repo.transaction():
                await session.execute(
                    text("""INSERT INTO auth_user(id,issuer,subject,roles,scopes)
                    VALUES (:id,'probe','alice','[]','[]')"""),
                    {"id": OWNER},
                )
                await repo.set_knowbase_session(
                    sid,
                    os.environ["SCRIPT_SOURCE_SESSION"],
                    datetime.now(UTC) + timedelta(minutes=3),
                )
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, "w") as package:
                package.writestr("SKILL.md", "Double the authorized input.")
                package.writestr(
                    "double.py",
                    "from pathlib import Path\nimport os\nvalue = int((Path(os.environ['SUNMOON_INPUT_DIR']) / 'source.txt').read_text())\nPath('outputs/result').write_text(str(value * 2))\n",
                )
            asset = await svc.create_skill(
                OWNER,
                SkillPackageCreate(
                    request_id="script-input-probe",
                    name="double",
                    description="Double an input",
                    version="1",
                    archive_base64=base64.b64encode(archive.getvalue()).decode(),
                ),
                package=True,
            )
            config = (await svc.prepare(OWNER, sid))["config"][
                "mcp_servers.sunmoon_capabilities"
            ]
            token = config["http_headers"]["Authorization"].removeprefix("Bearer ")
            args = {
                "path": "double.py",
                "inputs": [
                    {
                        "name": "source.txt",
                        "kind": "material",
                        "material_id": os.environ["SCRIPT_SOURCE_MATERIAL"],
                        "version_no": 1,
                        "reading": "text/1",
                    }
                ],
            }
            pending = await request_call(
                svc, sid, token, tool_key(asset["id"], "skill_run"), args
            )
            call_id = pending["call_id"]
            call = await repo.capability_call(OWNER, call_id)
            accepted = await svc.decide(OWNER, call_id, approval(call))
            assert accepted["status"] == "dispatching", accepted["detail"].get("result")
            async with asyncio.timeout(110):
                while True:
                    await svc.reconcile_scripts()
                    retained = await repo.capability_call(OWNER, call_id)
                    if retained["status"] != "dispatching":
                        break
                    await asyncio.sleep(0.4)
            assert retained["status"] == "succeeded", retained["detail"].get("result")
            (result,) = retained["detail"]["result"]["artifacts"]
            assert base64.b64decode(result["data_base64"]) == b"42"
            print(
                "KnowBase text/1 -> exact KnowBench approval -> isolated Job -> retained result 42",
                flush=True,
            )
    finally:
        try:
            if call_id:
                await executor.cancel(OWNER, call_id)
        finally:
            await database.aclose()


if __name__ == "__main__":
    for name in (
        "AGENT_TEST_DATABASE_URL",
        "DELIVERY_TEST_DATABASE_URL",
        "SCRIPT_TEST_PROVISIONER_URL",
    ):
        endpoint = urlsplit(os.environ[name])
        if endpoint.hostname not in ("localhost", "127.0.0.1") or (
            name.endswith("DATABASE_URL") and not endpoint.path.endswith("_tests")
        ):
            raise ValueError(f"{name} must point to an isolated local test environment")
    if (
        os.environ["AGENT_TEST_DATABASE_URL"]
        == os.environ["DELIVERY_TEST_DATABASE_URL"]
    ):
        raise ValueError("The two test databases must be separate")
    if len(sys.argv) == 1:
        asyncio.run(launch("knowbase", "source", os.environ.copy()))
    else:
        sys.path[:0] = [str(Path.cwd()), str(Path.cwd() / "tests")]
        asyncio.run({"source": source, "consume": consume}[sys.argv[1]]())
