"""使用试跑服务的内存仓，核对连续两次自动刷新覆盖的编号。"""
from dataclasses import replace
from uuid import UUID
from unittest.mock import AsyncMock
from tests.test_knowbot_questions import testing
from app.application.services.knowbot_service import REFRESH_BATCH


async def test_background_refresh_repeats_the_same_window(testing):
    svc, _, repo, _, _, _, run, _ = testing
    repo.tests.clear()
    for i in range(1, REFRESH_BATCH + 2):
        key = UUID(int=i)
        repo.tests[key] = replace(run, id=key, request_id=key)
    svc.refresh = AsyncMock()
    for _ in range(2):
        assert await svc.refresh_active() == REFRESH_BATCH
    visited = [call.args[0] for call in svc.refresh.await_args_list]
    assert visited[:REFRESH_BATCH] == visited[REFRESH_BATCH:]
    assert str(UUID(int=REFRESH_BATCH+1)) not in visited


async def test_refresh_final_test_after_runtime_reconciles_its_cost(testing):
    from app.domain.knowbots.test_run import RunResultV1

    svc, _, _, runtime, _, _, run, _ = testing
    def cancelled(spent):
        return RunResultV1(
            contract="knowbot-test-run/v1", run_id=run.run_id,
            status="cancelled", cost={"spent": spent},
        )
    runtime.results[run.run_id] = cancelled("1.00")
    first = await svc.refresh(str(run.id))
    assert first.report["cost"]["spent"] == "1.00"
    runtime.results[run.run_id] = cancelled("1.25")
    second = await svc.refresh(str(run.id))
    assert second.report["cost"]["spent"] == "1.00"
