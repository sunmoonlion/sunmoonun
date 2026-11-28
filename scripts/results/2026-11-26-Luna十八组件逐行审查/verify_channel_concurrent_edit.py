"""两个管理编辑均从同一版本开始；在隔离 PostgreSQL 控制其提交次序。"""
import asyncio
from dataclasses import replace
from test_durable_delivery_db import db as db
from app.application.supply.catalog import ChannelCatalog
from app.domain.supply.catalog import Registration
from app.infrastructure.repositories.supply_catalog import SqlCatalogRepository


async def test_rename_overwrites_already_saved_daily_cap(db):
    repo = SqlCatalogRepository(lambda: db)
    service = ChannelCatalog(repo)
    initial = Registration("旧称", "web", "web", ("webpage",), ("text",),
                           "self", 4, 20, domain="example.org")
    channel = await service.register("channel-example", initial, actor="first")
    waiting, resume = asyncio.Event(), asyncio.Event()

    class Delayed(SqlCatalogRepository):
        async def save_channel(self, *args, **kwargs):
            waiting.set()
            await resume.wait()
            await super().save_channel(*args, **kwargs)

    slow = ChannelCatalog(Delayed(lambda: db))
    rename = asyncio.create_task(slow.update(channel.id, replace(initial, name="新称"),
                                             actor="first", reason="更名"))
    try:
        await asyncio.wait_for(waiting.wait(), 5)
        await service.update(channel.id, replace(initial, daily_cap=300),
                             actor="second", reason="调整日上限")
        assert (await service.get(channel.id)).daily_cap == 300
    finally:
        resume.set()
        await rename
    final = await service.get(channel.id)
    assert final.name == "新称" and final.daily_cap == 20
    events = await repo.events(channel.id, limit=10)
    assert any(e.detail.get("daily_cap") == {"from": 20, "to": 300} for e in events)
    assert not any(e.detail.get("daily_cap") == {"from": 300, "to": 20} for e in events)
