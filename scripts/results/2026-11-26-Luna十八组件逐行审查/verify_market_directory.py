"""在 KnowMart 后端虚拟环境运行，仅依赖现有内存仓储。"""
import asyncio
import sys
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from unittest.mock import AsyncMock

backend = Path(__file__).resolve().parents[4] / "knowmart-app/knowmart-backend/app"
sys.path.insert(0, str(backend))
from app.application.services.expert_catalog import CatalogQuery
from tests.test_expert_catalog import ME, NOW, MemoryKnowbots, catalog, deliver


async def check():
    repo = MemoryKnowbots()
    bot = await deliver(repo, ME, "held-example")
    await deliver(repo, ME, "held-example", version="2")
    first, second = (repo.versions[(bot, v)] for v in ("1", "2"))
    repo.versions[(bot, "1")] = replace(first, delivered_at=NOW - timedelta(days=40))
    repo.versions[(bot, "2")] = replace(second, delivered_at=NOW, status="held")
    service = catalog(repo)
    market = AsyncMock()
    market.catalog_methods.return_value = [], {}
    all_items = await service.method_directory(ME, CatalogQuery(), "expert", market)
    recent = await service.method_directory(ME, CatalogQuery(updated="7d"), "expert", market)
    assert all_items["items"][0]["version"] == "2"
    assert all_items["items"][0]["updated_at"] == NOW.isoformat()
    assert recent["total"] == 0
    print("作者看到今天更新的 v2，加上近 7 天筛选后得到零条。")

    from sqlalchemy import create_engine, select
    from app.infrastructure.repositories.market import SqlMarketRepository
    from app.infrastructure.models.market import FormalListing, MethodClassification

    # Evaluate the real directory projection for the same frozen version in both scopes.
    with create_engine("sqlite://").begin() as conn:
        conn.exec_driver_sql("create table formal_method_listing(scope text, method_kind text, category text)")
        conn.exec_driver_sql(
            "insert into formal_method_listing values ('self','expert','uncategorized'),"
            "('public','expert','business.management')"
        )
        name = MethodClassification.__tablename__
        conn.exec_driver_sql(f"create table {name}(code text)")
        conn.exec_driver_sql(f"insert into {name} values ('analysis.statements')")
        from sqlalchemy import true
        rows = conn.execute(select(FormalListing.scope, SqlMarketRepository.directory_category())
                            .select_from(FormalListing).join(MethodClassification, true()))
        assert dict(rows.tuples().all()) == {"self": "analysis.statements", "public": "business.management"}
    print("同一专家的能力类目为报表核验，公开条目却只能按企业管理浏览。")


if __name__ == "__main__":
    asyncio.run(check())
