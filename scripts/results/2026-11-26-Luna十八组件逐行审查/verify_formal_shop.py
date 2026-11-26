"""复制至 KnowMart 后端 tests 中，以隔离 PostgreSQL 的 DELIVERY_TEST_DATABASE_URL 运行。"""
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
import pytest
from tests.test_shop_db import world, db
from tests.test_market_db import approved_publisher, SELLER, OPS, OTHER
from app.domain.market import FormalListingIn, ReviewDecision


@pytest.mark.parametrize("kind", ["tool", "expert"])
async def test_shop_with_only_a_formal_listing(world, kind):
    await approved_publisher(world)
    async def check(svc, admin):
        svc.formal_delivery = AsyncMock()
        svc.formal_delivery.check.return_value = {
            "title":"单据核对","method_kind":kind,"purpose":"交付差异清单",
            "skill_dependencies":[],"delivery_digest":"sha256:"+"a"*64,
        }
        listing = await svc.submit_formal(SELLER, FormalListingIn(
            reference={"method_id":str(uuid4()),"version":1,"digest":"sha256:"+"b"*64},
            category="tools.office",
        ))
        decision = await svc.review_formal(OPS,UUID(listing["listing_id"]),ReviewDecision(approve=True))
        assert decision["status"] == "listed"
        mine = await svc.my_shop(SELLER)
        assert mine["shop"]["listed"] is False
        assert (await svc.shops(q=None,category=None,sort="time",page=1))["total"] == 0
        detail = await svc.shop(OTHER,mine["shop"]["shop_id"])
        assert detail["shop"]["status"] == "open"
        assert not detail["experts"] and not detail["knowledge"]
        rows, _ = await svc.repo.catalog_methods(OTHER,kind,public=True,today=svc.now().date(),
            words="",since=None,codes=None,sort="name",offset=0,limit=10)
        assert [str(row["id"]) for row in rows] == [listing["listing_id"]]
    await world.run(check)
