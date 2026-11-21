"""Exercise both backends against disposable PostgreSQL, using no deployed accounts.

Run from knowbench-backend/app with AGENT_TEST_DATABASE_URL and DELIVERY_TEST_DATABASE_URL
pointing to disposable *_tests databases. Use .venv/bin/python -m pytest -c pyproject.toml
and pass this file's path. Each backend uses its own interpreter and migrated test schema.
"""

import asyncio
import json
import os
import sys
from copy import copy
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "knowbase-app/knowbase-backend/app"
BENCH = ROOT / "knowbench-app/knowbench-backend/app"


async def run_provider():
    import httpx
    from app.application.services.data_functions import DataFunctions
    from app.domain.user_data import Owner
    from fastapi import FastAPI, Header, HTTPException
    from test_durable_delivery_db import db
    from test_user_runs_db import World

    from app.interfaces.endpoints import user_run_routes as routes
    from app.interfaces.mcp import data_mcp
    from core.config import Settings

    schema = db.__wrapped__()
    factory = await anext(schema)
    try:
        from datetime import UTC, datetime

        world = World(factory)
        world.clock.now = datetime.now(UTC)
        material, _ = await world.upload("author", "report.txt", b"verified")
        await world.lib.show("author", material.id, "app:knowbench")
        public_key = json.loads(sys.stdin.readline())["public"]
        settings = Settings(
            knowbase_mcp_jwt_public_key=public_key, knowbase_mcp_jwt_issuer="knowbench"
        )
        mcp = data_mcp.DataMcp(
            DataFunctions(lambda: world.runs, lambda: None, lambda: world.lib)
        )
        app = FastAPI()
        app.include_router(data_mcp.build_router(settings, mcp), prefix="/api")
        app.include_router(routes.router, prefix="/api")

        def owner(authorization: str = Header()):
            if authorization != "Bearer owner-token":
                raise HTTPException(401)
            return Owner("author", "knowbench")

        app.dependency_overrides[routes.require_user_owner] = owner
        app.dependency_overrides[routes.get_user_run_service] = lambda: world.runs
        print(json.dumps({"material": material.id}), flush=True)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://localhost"
        ) as client:
            for line in sys.stdin:
                message = json.loads(line)
                response = await client.request(
                    message["method"],
                    message["path"],
                    json=message["body"],
                    headers={"Authorization": message["auth"]},
                )
                print(json.dumps([response.status_code, response.text]), flush=True)
    finally:
        await schema.aclose()


if __name__ == "__main__":
    if sys.argv[1:] != ["--provider"]:
        raise SystemExit(__doc__)
    sys.path[:0] = [str(BASE), str(BASE / "tests")]
    asyncio.run(run_provider())
else:
    sys.path[:0] = [str(BENCH), str(BENCH / "tests")]
    from test_workbench_ledger_db import db as db


async def test_method_read_across_services(db):
    import httpx
    from test_knowbase_method_read_db import (
        read_candidate,
        run_host_denial,
        run_host_tree,
        run_model_read,
    )

    from app.application.workbench.tokens import TokenIssuer, generate_private_key_pem
    from app.infrastructure.external.knowbase_data_v2 import KnowbaseDataV2

    assert (
        os.environ["DELIVERY_TEST_DATABASE_URL"].rsplit("/", 1)[-1].endswith("_tests")
    )
    issuer = TokenIssuer(generate_private_key_pem(), issuer="knowbench")
    provider = await asyncio.create_subprocess_exec(
        str(BASE / ".venv/bin/python"),
        __file__,
        "--provider",
        cwd=BASE,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )

    wire = asyncio.Lock()

    async def exchange(message):
        async with wire:
            provider.stdin.write((json.dumps(message) + "\n").encode())
            await provider.stdin.drain()
            line = await asyncio.wait_for(provider.stdout.readline(), timeout=30)
            return json.loads(line)

    try:
        material = await exchange({"public": issuer.public_pem()})

        async def forward(request):
            message = {
                "method": request.method,
                "path": request.url.path,
                "auth": request.headers["Authorization"],
                "body": json.loads(request.content) if request.content else None,
            }
            status, body = await exchange(message)
            rpc = message["body"] or {}
            if (
                rpc.get("method") == "tools/call"
                and not json.loads(body)["result"]["isError"]
            ):
                receipt = json.loads(body)["result"]["structuredContent"]["source"]
                # Keep the dispatch token intact. Changing only the input must fail.
                changed = json.loads(request.content)
                changed["params"]["arguments"]["material_id"] = str(uuid4())
                denied_status, denied = await exchange({**message, "body": changed})
                assert denied_status == 200 and json.loads(denied)["result"]["isError"]
                grant, leaf = receipt["grant_id"], receipt["method_call_id"]
                revoked, _ = await exchange(
                    {
                        "method": "DELETE",
                        "path": f"/api/internal/v2/user-data/run-grants/{grant}/method-read-consents/{leaf}",
                        "auth": "Bearer owner-token",
                        "body": None,
                    }
                )
                assert revoked == 204
                denied_status, denied = await exchange(message)
                assert denied_status == 200 and json.loads(denied)["result"]["isError"]
            return httpx.Response(status, content=body)

        client = KnowbaseDataV2(
            environ={"KNOWBASE_INTERNAL_URL": "https://localhost"},
            transport=httpx.MockTransport(forward),
        )
        client.material_id = material["material"]
        ctx, remote, sandbox = await read_candidate(db, (issuer, client))
        await run_host_tree(db, copy(ctx), client)
        for mode in ("missing", "revoked"):
            await run_host_denial(db, ctx, client, mode)
        for mode in ("allowed", "missing", "revoked"):
            await run_model_read(db, ctx, sandbox, client, mode)
        assert remote.calls == []
    finally:
        provider.stdin.close()
        try:
            assert await asyncio.wait_for(provider.wait(), timeout=30) == 0
        except TimeoutError:
            provider.kill()
            await provider.wait()
            raise
