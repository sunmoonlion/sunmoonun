"""Replay historical KnowLab transitions in a fresh, transaction-local schema."""
import os
import runpy
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, text


@pytest.fixture
def db():
    url = os.environ["DELIVERY_TEST_DATABASE_URL"]
    assert url.endswith("_tests")
    engine = create_engine(url.replace("postgresql://", "postgresql+psycopg://"))
    schema = "audit_" + uuid4().hex
    try:
        with engine.connect() as conn, conn.begin():
            conn.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
            conn.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
            with Operations.context(MigrationContext.configure(conn)):
                for path in sorted(Path("alembic/versions").glob("20*.py")):
                    module = runpy.run_path(str(path))
                    if module["revision"] == "20261024_0012":
                        yield conn, module
                        break
                    module["upgrade"]()
            conn.rollback()
    finally:
        engine.dispose()


def insert_drafts(conn, versions):
    request = uuid4()
    conn.execute(text("""INSERT INTO knowbot_request
        (id,owner_subject,title,runtime,idea,cases)
        VALUES (:id,'author','synthetic','knowbench','{}','[]')"""), {"id": request})
    for revision, version in enumerate(versions, 1):
        conn.execute(text("""INSERT INTO knowbot_draft
            (id,request_id,revision,version,status,manifest)
            VALUES (:id,:request,:revision,:version,'passed','{}')"""),
            dict(id=uuid4(), request=request, revision=revision, version=version))


def test_backfilled_unlisted_expert_can_downgrade(db):
    conn, migration = db
    insert_drafts(conn, ["1"])
    migration["upgrade"]()
    migration["downgrade"]()


@pytest.mark.parametrize("versions", [["1", "01"], ["0"], ["2147483648"]])
def test_preflight_reports_unrepresentable_expert_versions(db, versions):
    conn, migration = db
    insert_drafts(conn, versions)
    with pytest.raises(RuntimeError, match="0012 cannot backfill"):
        migration["_preflight"]()


def test_knowbase_only_dataset_downgrade_explains_required_recovery(db):
    conn, _ = db
    conn.execute(text("""INSERT INTO knowbot_dataset
        (id,owner_subject,name,version,content_type,size_bytes,sha256,knowbase_item_id)
        VALUES (:id,'author','synthetic','1','text/plain',1,:sha,'item-1')"""),
        {"id": uuid4(), "sha": "0" * 64})
    module = runpy.run_path(str(next(Path("alembic/versions").glob("*_0011_*.py"))))
    with pytest.raises(RuntimeError, match="knowbase"):
        module["downgrade"]()
