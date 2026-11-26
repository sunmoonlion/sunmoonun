"""在 KnowMart 后端 app 下以 PYTHONPATH=. 运行。"""
import asyncio
from datetime import datetime, UTC, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

from app.application.ports.knowbots import KnowbotRecord, KnowbotVersionRecord
from app.application.services.expert_catalog import ExpertCatalog, CatalogQuery
from app.domain.knowbots.manifest import SCHEMA_V3

async def main():
    now = datetime(2026, 11, 26, tzinfo=UTC)
    bot_id = uuid4()
    versions = tuple(
        KnowbotVersionRecord(bot_id, version, "digest", status, version, at, {"schema": SCHEMA_V3})
        for version, status, at in [("1","active",now-timedelta(days=40)),("2","held",now)]
    )
    repo = AsyncMock()
    repo.list_visible.return_value = [KnowbotRecord(bot_id,"owner","sample","对账","", "2",versions)]
    catalog = ExpertCatalog(repo, now=lambda: now)
    result = await catalog.list("owner", CatalogQuery())
    assert result["items"][0]["version"] == "2"
    assert result["items"][0]["updated_at"] == now.isoformat()
    assert (await catalog.list("owner", CatalogQuery(updated="7d")))["items"] == []

if __name__ == "__main__":
    asyncio.run(main())
