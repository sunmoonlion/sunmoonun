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
