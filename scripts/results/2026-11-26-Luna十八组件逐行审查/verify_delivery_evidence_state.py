"""KnowLab 交付服务的本地测试；Parts 用内存仓储和模拟的运行、市场适配器。"""
import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock

from app.domain.knowbots.test_run import CaseOutputsV1
from tests.test_knowbot_experts import OWNER, Parts, PUBLIC, SELF, user_token


async def lost_outputs():
    parts = Parts()
    def record_collection_failure(run_id, text):
        parts.runtime.case_outputs[run_id, "c1"] = CaseOutputsV1(
            contract="knowbot-test-run/v1", run_id=run_id, case_id="c1",
            error="取产出时平台出了错，这条用例的成稿与交回物没取到",
        )
    parts.clean_outputs = record_collection_failure
    _, expert, test = await parts.self_expert()
    [evidence] = await parts.repo.list_test_outputs(test.draft_id, test.run_id)
    assert evidence.outputs["error"] and evidence.outputs["deliverable"] is None
    delivery = await parts.deliveries.submit(OWNER, str(expert.id), SELF, user_token)
    assert delivery.auto_check["passed"] and not delivery.auto_check["findings"]


async def market_rotation():
    parts = Parts()
    for _ in range(2):
        _, expert, _ = await parts.self_expert()
        await parts.deliveries.submit(OWNER, str(expert.id), SELF, user_token)
    missing = None
    async def lookup(*, owner_subject, knowbot_ref):
        nonlocal missing
        if missing is None:
            missing = knowbot_ref
        return [] if knowbot_ref == missing else [{"version":"1","status":"active"}]
    parts.knowmart.versions = AsyncMock(side_effect=lookup)
    for _ in range(3):
        await parts.experts.sync_market(limit=1)
    calls = parts.knowmart.versions.await_args_list
    assert len(calls) == 3 and {call.kwargs["knowbot_ref"] for call in calls} == {missing}


async def remaining_budget():
    parts = Parts()
    _, expert, _ = await parts.self_expert()
    delivery = await parts.deliveries.submit(OWNER, str(expert.id), PUBLIC, user_token)
    first = await parts.deliveries.start_rerun(str(delivery.id), "operator")
    cost = Decimal("0.004")
    await parts.repo.update_test(first.id, status="platform_error", report={"cost":{"spent":str(cost),"currency":"CNY"}})
    await parts.deliveries.start_rerun(str(delivery.id), "operator")
    assigned = Decimal(parts.runtime.started[-1][1].budget.limit)
    assert assigned == Decimal("5.00")
    assert assigned + cost > delivery.budget_limit


if __name__ == "__main__":
    for case in (lost_outputs, market_rotation, remaining_budget):
        asyncio.run(case())
        print(case.__name__, "OK")
