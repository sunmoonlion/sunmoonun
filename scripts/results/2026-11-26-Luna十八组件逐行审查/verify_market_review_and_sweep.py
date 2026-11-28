"""两项市场业务回执。数据仅在测试专用 PostgreSQL schema。"""
from unittest.mock import patch

import pytest
from app.application.errors.exceptions import BadRequestError
from app.domain.market import ReportDecision, ReportIn
from tests.test_shop_db import BUYER, OTHER, db as db, demand, listed_knowledge, world as world
from tests.test_market_db import approved_publisher


async def test_report_writes_target_before_decision(world):
    row = await world.run(lambda svc, _: svc.create_demand(BUYER, demand()))
    target = row["demand_id"]
    case = await world.run(lambda svc, _: svc.report(
        OTHER, ReportIn(target_kind="demand", target_id=target, reason="核实请求")))
    async with world.db() as session:
        admin = world.admin(session)
        with patch.object(admin.repo, "update_report", side_effect=RuntimeError("decision write interrupted")):
            with pytest.raises(RuntimeError, match="interrupted"):
                await admin.decide_report(case["report_id"], ReportDecision(uphold=True), "operator")
    async with world.db() as session:
        repo = world.admin(session).repo
        assert (await repo.get_demand(target))["status"] == "taken_down"
        assert (await repo.get_report(case["report_id"]))["status"] == "open"


async def test_refused_batch_counts_as_checked(world):
    await approved_publisher(world)
    await listed_knowledge(world)
    async with world.db() as session:
        admin = world.admin(session)
        with patch.object(admin.vault, "offer_states", side_effect=BadRequestError("batch refused")):
            result = await admin.check_offers()
        assert result == {"checked": 1, "delisted": 0, "skipped": None}
