"""在不调用模型的情况下，用按游标分页的事件仓核对工作台即时读数。"""
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.application.workbench.expert_desk import ExpertDesk
from app.domain.workbench.states import TaskState
from app.domain.workbench.step_view import budget_view


async def test_a_long_step_stops_showing_recent_activity():
    events = [{"type": "turn/started", "cursor": i, "created_at": i, "payload": {}}
              for i in range(1, 1001)]
    events.append({"type": "turn/completed", "cursor": 1001, "created_at": 1001, "payload": {}})
    async def page(*, session_id, after_cursor, limit):
        return [e for e in events if e["cursor"] > after_cursor][:limit]
    repo = SimpleNamespace(
        list_task_events=AsyncMock(return_value=[{"attempt_id": "a", "cursor": 0, "created_at": 0}]),
        list_events=page, get_session=AsyncMock(return_value={"sandbox_id": "s"}),
        sandbox_held=AsyncMock(return_value=True), get_attempt=AsyncMock(return_value={"step_id": "one"}),
    )
    task = {"id":"task", "session_id":"sid", "state":TaskState.RUNNING, "current_step":0, "active_attempt_id":"a"}
    snapshot = await ExpertDesk(repo)._now(task, [{"index": 1, "title": "正在成稿"}])
    assert snapshot["last_event_at"] == 1000
    assert snapshot["doing"]["code"] == "thinking"


async def test_running_charge_disappears_during_the_same_attempts_question():
    repo = SimpleNamespace(list_record_events=AsyncMock(return_value=[
        {"type":"attempt/opened","attempt_id":"a"},
        {"type":"thread/tokenUsage/updated","payload":{"cost":{"turn":"0.50"}}},
    ]))
    task = {"id":"t","session_id":"s","active_attempt_id":"a","state":TaskState.RUNNING}
    desk = ExpertDesk(repo)
    def projection(running):
        return budget_view({"used":"1.00","currency":"CNY"}, running=running)["spent"]
    assert projection(await desk._running_cost(task)) == "1.50"
    task["state"] = TaskState.WAITING
    assert projection(await desk._running_cost(task)) == "1.00"
