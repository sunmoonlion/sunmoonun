"""PostgreSQL business-state checks. Events schedule two normal service calls."""
import asyncio
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError
from tests.test_shop_db import BUYER, OTHER, SELLER, db, demand, world
from app.domain.market import ResponseIn


@pytest.mark.asyncio
async def test_two_responses_remain_chosen(world):
    async def arrange(svc, admin):
        request = await svc.create_demand(BUYER, demand())
        did = request["demand_id"]
        a = await svc.respond(SELLER, did, ResponseIn(proposal="方案甲"))
        b = await svc.respond(OTHER, did, ResponseIn(proposal="方案乙"))
        return did, a["response_id"], b["response_id"]

    did, first, second = await world.run(arrange)
    async with world.db() as connection:
        svc = world.svc(connection)
        write_response = svc.repo.update_response
        async def interleave(*args, **kwargs):
            result = await world.run(lambda other, _: other.choose_response(BUYER, did, second))
            assert result["chosen_response_id"] == second
            await write_response(*args, **kwargs)
        with patch.object(svc.repo, "update_response", interleave):
            await svc.choose_response(BUYER, did, first)
    final = await world.run(lambda svc, _: svc.demand(BUYER, did))
    assert final["chosen_response_id"] == first
    assert {r["response_id"] for r in final["responses"] if r["status"] == "chosen"} == {first, second}


@pytest.mark.asyncio
async def test_parallel_house_rules_collide_on_version(world):
    ready = asyncio.Barrier(2)
    async def publish(text):
        async with world.db() as connection:
            admin = world.admin(connection)
            read = admin.repo.current_rules
            async def synchronized_read():
                row = await read()
                await asyncio.wait_for(ready.wait(), timeout=5)
                return row
            with patch.object(admin.repo, "current_rules", synchronized_read):
                return await admin.publish_rules(text, "operator")
    results = await asyncio.gather(publish("第一份"), publish("第二份"), return_exceptions=True)
    assert sum(isinstance(r, dict) for r in results) == 1
    assert sum(isinstance(r, IntegrityError) for r in results) == 1


@pytest.mark.asyncio
async def test_failed_empty_purchase_blocks_preexisting_material(world):
    from app.application.errors.exceptions import BadRequestError
    from app.domain.market import BuyIn
    from tests.test_market_db import approved_publisher, knowledge, token
    from tests.test_shop_db import listed_knowledge

    await approved_publisher(world)
    listing_id = await listed_knowledge(world)
    world.vault.offered["independent"] = dict(world.vault.offered["d1"])
    material = knowledge(items=[{"item_id": "independent"}])
    before = await world.run(lambda svc, _: svc.create_listing(BUYER, material, token))
    assert before["status"] == "draft"
    world.vault.gone = {"d1"}
    result = await world.run(lambda svc, _: svc.buy(BUYER, listing_id, BuyIn(request_id="empty-purchase")))
    assert result["status"] == "failed" and result["granted"] == []
    assert world.vault.holdings == {}
    with pytest.raises(BadRequestError) as failure:
        await world.run(lambda svc, _: svc.create_listing(BUYER, material, token))
    assert failure.value.code == "resale_not_allowed"
