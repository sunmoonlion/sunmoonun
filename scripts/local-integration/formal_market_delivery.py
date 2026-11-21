"""Run the two backends against disposable PostgreSQL databases on loopback.

Set AGENT_TEST_DATABASE_URL and DELIVERY_TEST_DATABASE_URL to separate *_tests
databases. Each side uses the repository's real migrations in a fresh schema.
External identity and the Skill execution receipt are synthetic.
"""

import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

SCRIPT = Path(__file__).resolve()
WORKSPACE = SCRIPT.parents[3]


async def serve_runtime(directory):
    import uvicorn
    from test_formal_method_admission_db import reviewed_skill_fixture
    from test_workbench_ledger_db import db

    from app.application.workbench.formal_methods import FormalMethods
    from app.bootstrap.api import create_app
    from app.infrastructure.security import relation_auth
    from app.infrastructure.workbench.repository import WorkbenchRepository
    from app.interfaces.endpoints import knowbot_runtime_routes
    from core.config import Settings

    database = db.__wrapped__()
    sessions = await anext(database)
    try:
        _, license, review, version = await reviewed_skill_fixture(sessions, "skill_script")

        async def service():
            async with sessions() as session:
                yield FormalMethods(
                    WorkbenchRepository(session),
                    source_licenses=(license,),
                    business_reviews=(review,),
                )

        class TestIssuer:
            async def verify_access_token(self, encoded, *, audience):
                assert (encoded, audience) == ("test-only-token", "test-market")
                return dict(
                    iss="test",
                    sub="test/market",
                    scope="knowbench:method-delivery",
                    iat=1,
                    exp=4102444800,
                )

        env = {
            "SERVICE_AUTH_METHOD_DELIVERY_CALLERS": "knowmart",
            "SERVICE_AUTH_METHOD_DELIVERY_KNOWMART_AUDIENCE": "test-market",
            "SERVICE_AUTH_METHOD_DELIVERY_KNOWMART_SUBJECT_ALLOWLIST": "test/market",
            "SERVICE_AUTH_METHOD_DELIVERY_KNOWMART_REQUIRED_SCOPE": "knowbench:method-delivery",
        }
        relation_auth.relation_verifier = lambda relation: (
            relation_auth.RelationServiceVerifier(
                relation, environ=env, oidc_client=TestIssuer(), settings=Settings()
            )
        )
        app = create_app(Settings())
        app.dependency_overrides[knowbot_runtime_routes.formal_methods] = service
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            server = uvicorn.Server(
                uvicorn.Config(
                    app,
                    log_level="error",
                    lifespan="off",
                    ssl_keyfile=str(directory / "key"),
                    ssl_certfile=str(directory / "cert"),
                )
            )
            task = asyncio.create_task(server.serve(sockets=[sock]))
            try:
                while not server.started:
                    if task.done():
                        await task
                        raise RuntimeError("Runtime stopped during startup")
                    await asyncio.sleep(0.1)
                status = directory / "starting"
                status.write_text(
                    json.dumps(
                        [
                            version.reference.model_dump(mode="json"),
                            sock.getsockname()[1],
                        ]
                    )
                )
                status.replace(directory / "ready")
                while not (directory / "done").exists():
                    await asyncio.sleep(0.1)
            finally:
                server.should_exit = True
                await task
    finally:
        await database.aclose()


async def buy_and_deliver(directory):
    from base64 import b64decode
    import httpx
    from tests.test_auth_routes_security import FakeAuthService, session
    from tests.test_knowbot_repository_db import db
    from tests.test_knowbot_routes import _caller
    from tests.test_market_db import Vault, World, approved_publisher
    from tests.test_market_routes import BASE, CSRF, ORIGIN, client

    from app.infrastructure.external.formal_method_delivery import FormalMethodDelivery
    from app.infrastructure.external.service_client import ServiceClient
    from app.infrastructure.security.relation_auth import require_summon_service
    from app.interfaces.endpoints import knowbot_routes, market_routes
    from app.interfaces.http.middleware import auth
    from app.main import app

    ref, port = json.loads((directory / "ready").read_text())
    os.environ["KNOWBENCH_INTERNAL_URL"] = (
        f"https://127.0.0.1:{port}/api/internal/v1/knowbot-runtime"
    )
    os.environ["SSL_CERT_FILE"] = str(directory / "cert")
    for key, value in {
        "CLIENT_ID": "local-test",
        "CLIENT_SECRET": "test-only",
        "SCOPE": "knowbench:method-delivery",
        "DISCOVERY_URL": "https://issuer.invalid/discovery",
        "BACKCHANNEL_ENDPOINT": "https://issuer.invalid/token",
    }.items():
        os.environ["KNOWBENCH_METHOD_DELIVERY_SERVICE_" + key] = value

    async def token(self):
        return "test-only-token"

    ServiceClient.token = token
    database = db.__wrapped__()
    sessions = await anext(database)
    try:
        world = World(sessions, Vault())
        await approved_publisher(world, subject="author")

        def login(subject, surface, scope):
            user = session(surface, scope)
            return user.model_copy(
                update={
                    "principal": user.principal.model_copy(update={"subject": subject})
                }
            )

        accounts = FakeAuthService(
            {
                "seller": login("author", "web", "profile:read"),
                "buyer": login("buyer", "web", "profile:read"),
                "ops": login("ops", "admin", "knowmart:admin"),
            }
        )
        auth.web_auth_service = auth.admin_auth_service = accounts

        async def service():
            async with sessions() as sql:
                svc = world.svc(sql)
                svc.formal_delivery = FormalMethodDelivery()
                svc.public_market = True
                yield svc

        app.dependency_overrides[market_routes._service] = service
        app.dependency_overrides[knowbot_routes.market_for_request] = service
        app.dependency_overrides[require_summon_service] = lambda: _caller("knowbench")
        web = {"Origin": ORIGIN, "X-CSRF-Token": CSRF}
        async with client("seller") as seller:
            created = await seller.post(
                BASE + "/formal-methods/listings",
                headers=web,
                json={"reference": ref, "category": "tools.office"},
            )
            created.raise_for_status()
            listing = created.json()["listing_id"]
        path = f"{BASE}/formal-methods/listings/{listing}/acquisitions"
        async with client("buyer") as buyer:
            assert (await buyer.post(path, headers=web)).status_code == 404
            async with client("ops", "sunmoonai_knowmart_admin_sid") as ops:
                reviewed = await ops.post(
                    f"/api/admin/v1/knowmart/market/formal-methods/listings/{listing}/review",
                    headers={"Origin": "http://localhost:5173", "X-CSRF-Token": CSRF},
                    json={"approve": True},
                )
                reviewed.raise_for_status()
            acquired = await buyer.post(path, headers=web)
            acquired.raise_for_status()
            receipt = acquired.json()
            assert receipt["reference"] == ref and "package" not in receipt
            assert receipt["skill_dependencies"][0]["terms"]["notices"] == ["原声明\n"]
            assert (await buyer.post(path, headers=web)).json() == receipt
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app), base_url="http://127.0.0.1"
        ) as runtime:
            for subject, expected in (("buyer", [ref]), ("other", [])):
                page = await runtime.post(
                    "/api/internal/v1/knowmart/formal-methods/planning-window",
                    json={"owner_subject": subject, "offset": 0, "limit": 8},
                )
                page.raise_for_status()
                assert page.json() == {
                    "owner_subject": subject,
                    "references": expected,
                    "more": False,
                }
            path = (
                f"/api/internal/v1/knowmart/formal-methods/listings/{listing}/delivery"
            )
            assert (
                await runtime.post(path, json={"buyer_subject": "other", "skill": ref})
            ).status_code == 404
            delivered = await runtime.post(
                path, json={"buyer_subject": "buyer", "skill": ref}
            )
            delivered.raise_for_status()
            files = {
                f["path"]: b64decode(f["data_base64"])
                for f in delivered.json()["package"]["files"]
            }
            assert files == {
                "SKILL.md": b"Read the notice",
                "summary.py": b"print(1)\n",
                "NOTICE": "原声明\n".encode(),
                "assets/demo.bin": bytes([255, 0]),
            }
            print("Verified one acquisition and four byte-identical Skill files.")
    finally:
        await database.aclose()


async def run():
    for key in ("AGENT_TEST_DATABASE_URL", "DELIVERY_TEST_DATABASE_URL"):
        url = urlsplit(os.environ.get(key, ""))
        if url.hostname not in ("localhost", "127.0.0.1") or not url.path.endswith(
            "_tests"
        ):
            raise ValueError(f"{key} must identify a local disposable *_tests database")

    def command(app, role, directory):
        cwd = WORKSPACE / f"{app}-app" / f"{app}-backend" / "app"
        return asyncio.create_subprocess_exec(
            str(cwd / ".venv/bin/python"),
            str(SCRIPT),
            role,
            str(directory),
            cwd=cwd,
            env={
                **os.environ,
                "NO_PROXY": "localhost,127.0.0.1",
                "no_proxy": "localhost,127.0.0.1",
            },
        )

    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        subprocess.run(
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
                str(directory / "key"),
                "-out",
                str(directory / "cert"),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        server = await command("knowbench", "runtime", directory)
        try:
            async with asyncio.timeout(90):
                while not (directory / "ready").exists():
                    if server.returncode is not None:
                        raise RuntimeError("Runtime setup failed")
                    await asyncio.sleep(0.1)
            market = await command("knowmart", "market", directory)
            try:
                if await asyncio.wait_for(market.wait(), 90):
                    raise RuntimeError("Market delivery check failed")
            finally:
                if market.returncode is None:
                    market.terminate()
                    await market.wait()
        finally:
            (directory / "done").touch()
            try:
                await asyncio.wait_for(server.wait(), 30)
            except TimeoutError:
                server.terminate()
                await server.wait()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        asyncio.run(run())
    else:
        sys.path[:0] = [str(Path.cwd()), str(Path.cwd() / "tests")]
        asyncio.run(
            {"runtime": serve_runtime, "market": buy_and_deliver}[sys.argv[1]](
                Path(sys.argv[2])
            )
        )
