"""Run using KnowBench pytest and two disposable *_tests database URLs.

The two backend applications run in separate interpreters. Only the HTTP wire
uses an in-process transport on each side of the subprocess pipe.
"""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "knowbase-app/knowbase-backend/app"
BENCH = ROOT / "knowbench-app/knowbench-backend/app"


async def provider():
    import httpx
    from fastapi import FastAPI
    from test_data_mcp import World, token
    from test_durable_delivery_db import db
    from app.application.services.query_facts_revision import query_facts_revision
    from app.domain.user_library import PUBLIC_OWNER
    from app.domain.user_runs import GrantRequestItem, InputPin
    from app.interfaces.http.internal.function_calls import build_function_router
    from core.config import Settings

    schema = db.__wrapped__()
    sessions = await anext(schema)
    try:
        world = World(sessions)
        material, version = await world.publish()

        async def grant(ref):
            return await world.runs.grant_by_user(
                "author",
                "knowbench",
                "delegation",
                ref,
                [
                    GrantRequestItem(
                        InputPin(material.id, 1, version.sha256), "public", PUBLIC_OWNER
                    )
                ],
            )

        await grant("native-comparison")
        expected = (
            await world.call(
                "query_facts",
                auth=token(sub="author"),
                scope="run",
                run="native-comparison",
            )
        )["facts"]
        assert len(expected) == 2 and {r["source"]["page"] for r in expected} == {88}
        settings = Settings(
            knowbase_mcp_jwt_public_key=json.loads(sys.stdin.readline())["public"],
            knowbase_mcp_jwt_issuer="knowbench",
        )
        app = FastAPI()
        app.include_router(
            build_function_router(settings, world.functions), prefix="/api"
        )
        print(json.dumps([query_facts_revision(), expected]), flush=True)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://localhost"
        ) as http:
            for line in sys.stdin:
                msg = json.loads(line)
                if "grant" in msg:
                    reply = (await grant(msg["grant"])).id
                else:
                    res = await http.post(
                        msg["path"],
                        json=msg["body"],
                        headers={"Authorization": msg["auth"]},
                    )
                    reply = [res.status_code, res.text]
                print(json.dumps(reply), flush=True)
    finally:
        await schema.aclose()


if __name__ == "__main__":
    sys.path[:0] = [str(BASE), str(BASE / "tests")]
    asyncio.run(provider())
else:
    sys.path[:0] = [str(BENCH), str(BENCH / "tests")]
    from test_workbench_ledger_db import db as db


async def test_registered_function_and_expert_with_actual_knowbase(db):
    import httpx
    from test_formal_function_db import exercise_function
    from app.application.workbench.tokens import TokenIssuer, generate_private_key_pem
    from app.domain.workbench.service_functions import FunctionRevision

    issuer = TokenIssuer(generate_private_key_pem(), issuer="knowbench")
    process = await asyncio.create_subprocess_exec(
        str(BASE / ".venv/bin/python"),
        __file__,
        cwd=BASE,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )

    async def exchange(msg):
        process.stdin.write((json.dumps(msg) + "\n").encode())
        await process.stdin.drain()
        line = await asyncio.wait_for(process.stdout.readline(), timeout=45)
        assert line, "KnowBase fixture stopped"
        return json.loads(line)

    try:
        revision, expected = await exchange({"public": issuer.public_pem()})

        async def forward(req):
            status, body = await exchange(
                {
                    "path": req.url.path,
                    "body": json.loads(req.content),
                    "auth": req.headers["Authorization"],
                }
            )
            return httpx.Response(status, content=body)

        async def grant(ref):
            await exchange({"grant": ref})

        await exercise_function(
            db,
            FunctionRevision.model_validate(revision),
            issuer,
            expected,
            forward=forward,
            grant=grant,
        )
    finally:
        process.stdin.close()
        await process.stdin.wait_closed()
        assert await asyncio.wait_for(process.wait(), timeout=45) == 0
