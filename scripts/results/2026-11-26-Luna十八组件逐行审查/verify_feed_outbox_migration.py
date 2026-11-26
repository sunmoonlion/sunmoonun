"""在独立测试库的事务中执行 0001–0007，比较迁移前后的待投递消息。"""
import runpy
from uuid import uuid4

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text
from tests.test_durable_delivery_db import ROOT, db as db


def compare(connection):
    schema = "audit_" + uuid4().hex
    connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
    connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}",public')
    with Operations.context(MigrationContext.configure(connection)):
        for path in sorted((ROOT / "alembic/versions").glob("20*.py"))[:7]:
            if "_0007_" in path.name:
                for statement in (
                    """INSERT INTO info_document(id,title,status,metadata_json)
                    VALUES(gen_random_uuid(),'subject','fresh','{}')""",
                    """INSERT INTO info_document_version(id,document_id,version_no,source_url,
                    title,content_hash,extraction_status,metadata_json)
                    SELECT gen_random_uuid(),id,1,'urn:test','title','digest','ok','{}' FROM info_document""",
                    """INSERT INTO distribution_record(id,document_id,document_version_id,target_app,
                    content_hash,status,payload) SELECT gen_random_uuid(),document_id,id,'demo',
                    content_hash,'pending','{}' FROM info_document_version""",
                    """INSERT INTO delivery_outbox_message(topic,aggregate_id,aggregate_type,idempotency_key)
                    SELECT t,id,'distribution','same-key' FROM distribution_record
                    CROSS JOIN (VALUES ('alpha'),('beta')) topics(t)""",
                ):
                    connection.execute(text(statement))
            runpy.run_path(str(path))["upgrade"]()
    for table, expected in (("delivery_outbox_message_legacy", 2), ("outbox_message", 1)):
        assert connection.scalar(text(f"SELECT count(*) FROM {table} WHERE topic IN ('alpha','beta')")) == expected


async def test_pending_across_topics(db):
    async with db() as session:
        conn = await session.connection()
        await conn.run_sync(compare)
        await session.rollback()
