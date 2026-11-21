"""KnowBase publisher -> KnowBench API -> PostgreSQL -> KnowLab incubation source query.

Run with the KnowBench venv pytest and AGENT_TEST_DATABASE_URL pointing to a *_tests DB.
Only OIDC token issuance and verification use synthetic credentials.
"""

import asyncio
import os
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / "knowbench-app/knowbench-backend/app"
BASE = ROOT / "knowbase-app/knowbase-backend/app"


async def provider(origin):
    from app.bootstrap.publish_functions import publish_query_facts
    from app.infrastructure.external.downstream_service import DownstreamServiceClient
    from core.config import Settings

    class Issuer:
        async def exchange_client_credentials(self, *, scope, client_id, client_secret):
            assert (scope, client_id, client_secret) == (
                "knowbench:function-publish",
                "knowbase",
                "fixture",
            )
            return {"access_token": "knowbase", "expires_in": 60}

    client = DownstreamServiceClient(
        Settings(
            _env_file=None,
            downstream_scope="knowbench:function-publish",
            downstream_client_id="knowbase",
            downstream_client_secret="fixture",
            downstream_base_url=origin,
            downstream_allowed_path_prefixes="/api/internal/v1/method-skill-center/functions",
        ),
        oidc_client=Issuer(),
    )
    print(await publish_query_facts(client))


if __name__ == "__main__":
    sys.path.insert(0, str(BASE))
    asyncio.run(provider(sys.argv[1]))
else:
    sys.path[:0] = [str(BENCH), str(BENCH / "tests")]
    from test_workbench_ledger_db import db as db


async def test_service_publication_and_selection(db, monkeypatch):
    import httpx
    import uvicorn
    from uuid import uuid4
    from sqlalchemy import text
    from test_formal_method_routes import FakeOidc, HEADERS
    from test_service_function_publication_db import Claims
    from test_source_licenses import license_record
    from app.application.workbench.formal_methods import FormalMethods
    from app.bootstrap.api import create_app
    from app.infrastructure.security import relation_auth
    from app.infrastructure.storage.postgres import get_db_session
    from app.infrastructure.workbench.repository import WorkbenchRepository
    from app.interfaces.endpoints import knowbot_runtime_routes as routes
    from core.config import Settings

    assert os.environ["AGENT_TEST_DATABASE_URL"].endswith("_tests")
    app = create_app(Settings())
    verifier = relation_auth.RelationServiceVerifier(
        "function-publish",
        settings=Settings(),
        oidc_client=Claims(),
        environ={
            "SERVICE_AUTH_FUNCTION_PUBLISH_CALLERS": "knowbase",
            "SERVICE_AUTH_FUNCTION_PUBLISH_KNOWBASE_SUBJECT_ALLOWLIST": "knowbase",
            "SERVICE_AUTH_FUNCTION_PUBLISH_KNOWBASE_AUDIENCE": "publish",
            "SERVICE_AUTH_FUNCTION_PUBLISH_KNOWBASE_REQUIRED_SCOPE": "knowbench:function-publish",
        },
    )
    monkeypatch.setitem(relation_auth._verifiers, "function-publish", verifier)

    async def database():
        async with db() as s:
            yield s

    licenses = []

    async def methods():
        async with db() as s:
            yield FormalMethods(WorkbenchRepository(s), source_licenses=licenses)

    app.dependency_overrides[get_db_session] = database
    app.dependency_overrides[routes.formal_methods] = methods
    read_verifier = relation_auth.RelationServiceVerifier(
        "testrun",
        settings=Settings(),
        oidc_client=FakeOidc(),
        environ={
            "SERVICE_AUTH_TESTRUN_CALLERS": "knowlab",
            "SERVICE_AUTH_TESTRUN_KNOWLAB_SUBJECT_ALLOWLIST": "admin/lab",
            "SERVICE_AUTH_TESTRUN_KNOWLAB_AUDIENCE": "lab-aud",
            "SERVICE_AUTH_TESTRUN_KNOWLAB_REQUIRED_SCOPE": "knowbench:testrun",
        },
    )
    monkeypatch.setitem(relation_auth._verifiers, "testrun", read_verifier)
    async with db() as s, s.begin():
        await s.execute(
            text(
                "INSERT INTO auth_user(id, issuer, subject, roles, scopes) VALUES (:id,'test','author','[]','[]')"
            ),
            {"id": uuid4()},
        )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        origin = f"http://127.0.0.1:{sock.getsockname()[1]}"
        server = uvicorn.Server(
            uvicorn.Config(
                app, lifespan="off", access_log=False, log_level="error", ws="none"
            )
        )
        serving = asyncio.create_task(server.serve(sockets=[sock]))
        try:
            async with asyncio.timeout(10):
                while not server.started:
                    if serving.done():
                        await serving
                        raise RuntimeError("Test server stopped during startup")
                    await asyncio.sleep(0.05)
            proc = await asyncio.create_subprocess_exec(
                str(BASE / ".venv/bin/python"),
                __file__,
                origin,
                stdout=asyncio.subprocess.PIPE,
                cwd=BASE,
                env={**os.environ, "no_proxy": "127.0.0.1", "NO_PROXY": "127.0.0.1"},
            )
            try:
                out, _ = await asyncio.wait_for(proc.communicate(), 30)
            finally:
                if proc.returncode is None:
                    proc.kill()
                    await proc.wait()
            assert proc.returncode == 0
            digest = out.decode().strip()
            path = "/api/internal/v1/knowbot-runtime/users/author/formal-method-sources"
            async with httpx.AsyncClient(
                base_url=origin, trust_env=False, headers=HEADERS
            ) as http:
                assert (await http.get(path)).json() == {"items": []}
                pin = {
                    "source": "knowbase",
                    "entry": "query_facts",
                    "version": "1",
                    "kind": "service_function",
                    "digest": digest,
                }
                record = license_record(pin)
                licenses.append(record)
                res = await http.get(path)
                assert res.status_code == 200, res.text
                [source] = res.json()["items"]
                assert (
                    pin.items() <= source.items()
                    and source["license_basis"] == record.basis
                )
                licenses.clear()
                assert (await http.get(path)).json() == {"items": []}
        finally:
            server.should_exit = True
            await serving
