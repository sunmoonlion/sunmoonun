"""复测 KnowLab 补采完成后出现多候选，以及批量签授权中途失败。仅使用本地测试替身。"""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

backend = Path(__file__).resolve().parents[4] / "knowlab-app/knowlab-backend/app"
sys.path.insert(0, str(backend))

from app.application.errors.exceptions import ServiceUnavailableError
from app.application.services.knowbot_test_data import KnowbotTestData
from app.domain.knowbots.data_plan import _pin
from tests.test_knowbot_test_data import OWNER, candidate, token, world


async def ambiguous_after_supply():
    service, data, repo, runtime, kb, supply, _, test = await world.__wrapped__()
    [shown] = await data.pending(OWNER, str(test.id), token)
    await data.confirm(OWNER, shown["question_id"], token)
    fresh = kb._latest()
    fresh["items"][1].update(
        status="ambiguous",
        chosen=[],
        candidates=[candidate("2024"), {**candidate("2024"), "material_id": "alternate"}],
    )
    kb.refresh = AsyncMock(return_value=fresh)
    supply.status = "ready"
    await service.refresh(str(test.id))
    [question] = repo.questions.values()
    state = question.data_state
    assert state["status"] == "answered" and state["incomplete"] == []
    assert [p["material_id"] for p in state["pins"]] == ["m-2025"]
    assert len(runtime.answers) == 1
    print("2024 年资料仍需选择；只带 2025 年资料回答，缺项记录为空。")


async def partial_grant_failure():
    sample = _pin(candidate("2025"))
    cases = {name: {"items": [sample]} for name in ("a", "b")}
    repo = AsyncMock()
    repo.latest_test_set.return_value = SimpleNamespace(cases=cases, version=1)
    kb = AsyncMock()
    kb.case_grant.side_effect = ["g-first", ServiceUnavailableError("fixture")]
    data = KnowbotTestData(repo, kb, None, None, supply_enabled=False, max_wait_seconds=600)
    try:
        await data.with_test_set(
            SimpleNamespace(id="fixture", owner_subject=OWNER),
            [{"case_id": key} for key in cases],
            run_id="fixture",
            ttl_seconds=600,
        )
    except ServiceUnavailableError:
        assert kb.case_grant.await_count == 2
        kb.revoke_case_grant.assert_not_awaited()
    else:
        raise AssertionError("未触发第二例故障")
    print("第二例签发失败，首例已获授权，本次没有撤销调用。")


if __name__ == "__main__":
    asyncio.run(ambiguous_after_supply())
    asyncio.run(partial_grant_failure())
