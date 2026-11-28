"""在 KnowFeed 后端 app 下用项目 Python 运行。仅使用内存仓库替身。"""
import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

from app.application.supply.demands import DemandService
from app.application.supply.matching import PreMatch
from app.domain.supply.models import DemandItemIn, DescriptionKey, SupplyError
from app.domain.supply.prematch import PrematchRequestV1


async def check():
    repo, catalog, schedule = AsyncMock(), AsyncMock(), AsyncMock()
    repo.channels.return_value = []
    schedule.queue_ahead.return_value = schedule.fetched_today.return_value = {}
    matching = PreMatch(repo, catalog, schedule, global_rate=10)
    first = {"ref": "annual", "key": {"subject": "000858.SZ", "doc_type": "annual_report"}}
    second = {"ref": "lookup", "key": {"doc_type": "other_text", "source_query": {}}}
    one = await matching.check("knowlab", PrematchRequestV1(items=[first]))
    assert len(one) == 1 and one[0].ref == "annual"
    try:
        await matching.check("knowlab", PrematchRequestV1(items=[first, second]))
    except SupplyError as exc:
        assert exc.code == "query_invalid"
    else:
        raise AssertionError("expected whole batch to lose its first result")

    key = DescriptionKey("000858.SZ", "annual_report")
    kb = AsyncMock()
    kb.check_confirmation.return_value = {"items": [{"item_id": "c1", "key": key.as_dict()}]}
    repo.find_demand.return_value = None
    repo.items_of.return_value = []
    service = DemandService(repo, kb)
    args = dict(app="knowbench", owner="author", proposer="user", chain=(),
                task_ref="task", confirmation_id="confirm", idempotency_key="annual-report-001",
                items=[DemandItemIn(key, ("original",), "c1")])
    due = datetime(2026, 11, 26, tzinfo=UTC)
    prior, _, replay = await service.submit(**args, deadline=due, note="第一版")
    assert not replay and prior.deadline == due
    repo.find_demand.return_value = prior
    for deadline, note in ((due + timedelta(days=1), "第一版"), (due, "修订版")):
        returned, _, replay = await service.submit(**args, deadline=deadline, note=note)
        assert replay and returned.deadline == due and returned.note == "第一版"


asyncio.run(check())
