"""Recovery must resolve the original run before a retry is dispatched."""
from datetime import timedelta

import pytest

from tests.test_knowbot_creation_service import _reviewed_draft, parts


@pytest.mark.asyncio
async def test_retry_after_timeout_cancels_the_original(parts):
    svc, repo, runtime, clock = parts
    _, draft = await _reviewed_draft(svc)
    first = await svc.start_test(str(draft.id), budget_limit="20", timeout_seconds=600)
    clock.at += timedelta(minutes=16)
    await svc.reset_stuck(str(first.id))
    second = await svc.start_test(str(draft.id), budget_limit="20", timeout_seconds=600)
    assert repo.tests[first.id].status == "platform_error"
    assert [body.run_id for _, body in runtime.started] == [first.run_id, second.run_id]
    assert first.run_id in runtime.cancelled
