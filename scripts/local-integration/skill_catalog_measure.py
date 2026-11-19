"""Measure the KnowBench catalog before and after 0046 on the same disposable DB.

Run in each revision's backend app directory with its test dependencies.
Set AGENT_TEST_DATABASE_URL to a dedicated *_tests database. Run seed and before
with the old checkout, then migrate, after and instructions with the candidate. The seed refuses
to overwrite its schema. The comparison uses synthetic files and local HTTP ASGI.
"""

import asyncio
import hashlib
import importlib.util
import json
import math
import os
import random
import statistics
import sys
from pathlib import Path
from time import perf_counter_ns

import psycopg
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import create_async_engine

APP = Path.cwd()
sys.path[:0] = [str(APP), str(APP / "tests")]

SCHEMA = "luna_skill_catalog_measure"
OWNER = "68767bed-c759-42a6-95a0-fb2cf23672ea"


def reconcile(conn, before):
    assets = conn.execute(
        text(
            "SELECT id,owner_actor_id,name,status,revision,default_selected,request_id,"
            "request_digest,created_at,updated_at,detail->>'digest' FROM workbench_capability_assets "
            "WHERE kind='skill' ORDER BY id"
        )
    ).all()
    if before:
        query = """SELECT id, 'SKILL.md' AS path, convert_to(detail->>'content','UTF8') AS data
                   FROM workbench_capability_assets WHERE detail->>'format'='instruction-markdown'
                   UNION ALL SELECT id, key, decode(value,'base64') FROM workbench_capability_assets,
                   LATERAL jsonb_each_text(detail->'resources') ORDER BY 1,2"""
    else:
        query = "SELECT asset_id,path,data FROM workbench_skill_files ORDER BY 1,2"
    files = [
        (str(i), p, len(raw), hashlib.sha256(raw).hexdigest())
        for i, p, raw in conn.execute(text(query))
    ]
    manifest = json.dumps([[list(a) for a in assets], files], default=str).encode()
    return {
        "assets": len(assets),
        "files": len(files),
        "raw_bytes": sum(f[2] for f in files),
        "manifest_sha256": hashlib.sha256(manifest).hexdigest(),
    }


async def seed(factory):
    from test_capabilities_db import service
    from test_skill_package import archive

    from app.domain.workbench.capabilities import SkillCreate
    from app.domain.workbench.skill_package import SkillPackageCreate
    from app.infrastructure.workbench.repository import WorkbenchRepository

    rng = random.Random(46)
    async with factory() as session:
        svc = service(WorkbenchRepository(session))
        for i in range(40):
            common = dict(
                request_id=f"measure-skill-{i}",
                name=f"skill-{i}",
                version="1",
                description="Catalog measurement fixture",
            )
            body = rng.randbytes(16384).hex()
            if i < 8:
                await svc.create_skill(OWNER, SkillCreate(**common, content=body))
            else:
                encoded = archive(
                    {
                        "SKILL.md": body,
                        "guide.txt": "Sample",
                        "assets/input.bin": rng.randbytes(131072),
                    }
                )
                await svc.create_skill(
                    OWNER,
                    SkillPackageCreate(**common, archive_base64=encoded),
                    package=True,
                )


async def measure(engine, factory, url, *, instructions):
    import test_capability_routes_db as routes

    routes.OWNER = OWNER  # Both revisions must load the same synthetic account.
    endpoint = "/api/workbench/capabilities"
    if instructions:
        async with engine.connect() as conn:
            skill_id = (
                await conn.execute(
                    text(
                        "SELECT id FROM workbench_capability_assets WHERE owner_actor_id=:owner AND name='skill-8'"
                    ),
                    {"owner": OWNER},
                )
            ).scalar_one()
        endpoint += f"/skills/{skill_id}/instructions"
    queries = []

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def capture(conn, cursor, statement, parameters, context, many):
        queries.append((statement, parameters))

    app = routes.application(factory, None)
    times = []
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as http:
        for i in range(35):
            queries.clear()
            start = perf_counter_ns()
            response = await http.get(endpoint)
            ms = (perf_counter_ns() - start) / 1e6
            response.raise_for_status()
            body = response.json()
            assert len(body) == 32768 if instructions else len(body["assets"]) == 40
            assert len(queries) == 1
            if i >= 5:
                times.append(ms)
    # Replay the observed app SELECT in binary format and count field payload
    # bytes from libpq. Excludes protocol headers, NULL markers and HTTP headers.
    sql, params = queries[0]
    with psycopg.connect(url, options=f"-csearch_path={SCHEMA}") as conn:
        with psycopg.RawCursor(conn) as cursor:
            cursor.execute(sql, params, binary=True)
            result = cursor.pgresult
            assert result.ntuples == (1 if instructions else 40)
            db_bytes = sum(
                len(result.get_value(r, c) or b"")
                for r in range(result.ntuples)
                for c in range(result.nfields)
            )
    return {
        "warmups": 5,
        "samples": len(times),
        "sql_calls_per_request": len(queries),
        "sql_result_field_bytes": db_bytes,
        "http_body_bytes": len(response.content),
        "p50_ms": round(statistics.median(times), 3),
        "p95_ms": round(sorted(times)[math.ceil(0.95 * len(times)) - 1], 3),
    }


async def main():
    from test_workbench_ledger_db import migrate

    from app.infrastructure.storage.postgres import make_session_factory

    (phase,) = sys.argv[1:]
    if phase not in ("seed", "before", "migrate", "after", "instructions"):
        raise ValueError("Expected seed, before, migrate, after or instructions")
    url = os.environ["AGENT_TEST_DATABASE_URL"]
    if not url.rsplit("/", 1)[-1].endswith("_tests"):
        raise ValueError("Use a disposable *_tests database")
    sync = create_engine(url.replace("postgresql://", "postgresql+psycopg://"))
    with sync.begin() as conn:
        if phase == "seed":
            conn.execute(text(f"CREATE SCHEMA {SCHEMA}"))
        conn.execute(text(f"SET LOCAL search_path TO {SCHEMA}"))
        if phase == "seed":
            migrate(conn)
        elif phase == "migrate":
            old = reconcile(conn, True)
            path = APP / "alembic/versions/20261119_0046_skill_files.py"
            spec = importlib.util.spec_from_file_location("skill_migration", path)
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)
            with Operations.context(MigrationContext.configure(conn)):
                migration.upgrade()
            new = reconcile(conn, False)
            assert old == new
            print(json.dumps({"before": old, "after": new}))
            return
    engine = create_async_engine(
        url.replace("postgresql://", "postgresql+asyncpg://"),
        connect_args={"server_settings": {"search_path": SCHEMA}},
    )
    try:
        factory = make_session_factory(engine)
        if phase == "seed":
            await seed(factory)
        else:
            print(
                json.dumps(
                    await measure(
                        engine, factory, url, instructions=phase == "instructions"
                    )
                )
            )
    finally:
        await engine.dispose()
        sync.dispose()


if __name__ == "__main__":
    asyncio.run(main())
