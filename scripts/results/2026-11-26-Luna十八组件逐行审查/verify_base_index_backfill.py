"""Exercise historical knowledge indexing migration on a disposable database."""
import os
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from test_drop_legacy_data_db import _run
from test_durable_delivery_db import ROOT
from test_retrieval_migration import _load_migration_module


def test_empty_legacy_prefix_uses_recorded_provider_dataset():
    module = _load_migration_module()
    row = {"legacy_knowledge_document_id": "ragflow-dataset:",
           "status_history": [{"metadata": {"ragflow_dataset_id": "verified-id"}}]}
    assert module._provider_dataset_id(row) == "verified-id"


@pytest.mark.asyncio
async def test_unknown_digest_is_not_presented_as_a_verified_indexed_version():
    url = make_url(os.environ["DELIVERY_TEST_DATABASE_URL"])
    assert url.database.endswith("_tests")
    engine = create_async_engine(url.set(drivername="postgresql+asyncpg"))
    versions = sorted((ROOT / "alembic/versions").glob("20*.py"))[:3]
    try:
        async with engine.connect() as conn:
            async with conn.begin():
                schema = "audit_" + uuid.uuid4().hex
                await conn.execute(text(f"CREATE SCHEMA {schema}"))
                await conn.execute(text(f"SET LOCAL search_path TO {schema}, public"))
                await conn.run_sync(_run, versions[:2])
                await conn.execute(text("""
                    INSERT INTO knowledge_ingestion_job
                    (id,source_app,source_document_id,source_document_version_id,profile_key,
                     idempotency_key,source_artifact_refs,metadata_json,payload,status,status_history,
                     knowledge_document_id,ragflow_document_id)
                    VALUES(gen_random_uuid(),'knowfeed',gen_random_uuid(),gen_random_uuid(),
                    'test','audit','[]','{}','{}','succeeded','[]','ragflow-dataset:dataset','doc')
                """))
                await conn.run_sync(_run, versions[2:])
                row = (await conn.execute(text("SELECT status,content_hash FROM knowledge_document_version"))).one_or_none()
                assert row is None or row.status != "indexed" or row.content_hash != "0"*64
                await conn.rollback()
    finally:
        await engine.dispose()
