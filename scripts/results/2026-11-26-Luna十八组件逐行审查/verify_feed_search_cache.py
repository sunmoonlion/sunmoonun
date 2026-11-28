"""检查相同主题扩大候选数、缩小网站范围、勾选中断恢复。仅用离线渠道。"""
from datetime import timedelta
from unittest.mock import patch
import pytest
from tests.test_supply_subscriptions_db import Subs, _search_channel, db as db
from app.domain.supply.models import SupplyError


async def test_larger_search_reuses_short_result(db):
    world = Subs(db)
    await _search_channel(world)
    await world.searches.start("alice", "工业", (), 1)
    await world.run_all()
    larger = await world.searches.start("alice", "工业", (), 2)
    assert larger.status == "ready" and len(larger.candidates) == 1
    world.w.clock.now += timedelta(minutes=11)
    fresh = await world.searches.start("alice", "工业", (), 2)
    await world.run_all()
    assert len((await world.searches.get("alice", fresh.id)).candidates) == 2


async def test_requested_child_site_gets_parent_site_results(db):
    world = Subs(db)
    await _search_channel(world)
    search = await world.searches.start("alice", "工业", ("reports.www.stats.gov.cn",), 2)
    await world.run_all()
    found = await world.searches.get("alice", search.id)
    assert len(found.candidates) == 2
    assert all(c["url"].startswith("https://www.stats.gov.cn/") for c in found.candidates)


async def test_interrupted_pick_before_confirmation_stays_ended(db):
    world = Subs(db)
    await _search_channel(world)
    search = await world.searches.start("alice", "工业", (), 1)
    await world.run_all()
    async def pick():
        return await world.searches.pick("token", "alice", search.id, ["k1"],
            readings=("original",), idempotency_key="sample-retry-01")
    class Stopped(BaseException):
        pass
    with patch.object(world.user, "confirm", side_effect=Stopped), pytest.raises(Stopped):
        await pick()
    world.w.clock.now += timedelta(days=1)
    with pytest.raises(SupplyError) as caught:
        await pick()
    assert caught.value.code == "search_not_ready"
    assert (await world.searches.get("alice", search.id)).status == "ended"
