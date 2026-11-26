"""运行于 KnowFeed 的一次性 PostgreSQL 测试库。对象存储是本地内存替身。"""
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

from test_durable_delivery_db import db as db
from app.application.supply.retention import OriginalRetention
from app.domain.supply.models import Original
from app.infrastructure.repositories.supply import SqlSupplyRepository
from app.infrastructure.repositories.supply_catalog import SqlCatalogRepository


async def test_new_delivery_renews_record_while_purger_deletes_bytes(db):
    now = datetime.now(UTC)
    content = b"local retention test"
    original = Original(str(uuid4()), sha256(content).hexdigest(), "test", "document",
                        "https://example.org/doc", "text/plain", len(content),
                        "original/document", now - timedelta(days=31),
                        purge_after=now - timedelta(seconds=1))
    repo = SqlSupplyRepository(lambda: db)
    await repo.save_original(original, {})
    objects = {original.object_key: content}
    renewed = now + timedelta(days=30)

    class Store:
        async def delete(self, key):
            await repo.mark_delivered(original.id, now, renewed)
            del objects[key]

    service = OriginalRetention(SqlCatalogRepository(lambda: db), Store(), clock=lambda: now)
    assert await service.purge_due() == 0
    row = await repo.find_original(original.sha256)
    assert row.purged_at is None and row.purge_after == renewed
    assert row.object_key not in objects
