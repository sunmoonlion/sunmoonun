"""在隔离 PostgreSQL 中依次发生提问、旧轮正常结算、作者回答。"""
from decimal import Decimal

import pytest
from test_pending_method_usage_db import pending
from test_workbench_ledger_db import OWNER
from test_workbench_ledger_db import db as db

from app.application.workbench.ledger import Ledger
from app.domain.workbench.errors import InteractionRejected
from app.domain.workbench.models import InteractionPrompt
from app.domain.workbench.states import WaitingReason
from app.infrastructure.workbench.repository import WorkbenchRepository


async def test_final_bill_invalidates_unrelated_open_question(db):
    _, task, prior = await pending(db)
    async with db() as session:
        repo = WorkbenchRepository(session)
        ledger = Ledger(repo)
        question = await ledger.open_interaction(
            task, kind="input", waiting_reason=WaitingReason.INPUT,
            prompt=InteractionPrompt(title="核对年度", question="哪一年度？"),
        )
        await ledger.record_late_cost(
            task, attempt_id=prior, consumed=Decimal("1.25"),
            tokens={}, turn_id="pending-turn",
        )
        with pytest.raises(InteractionRejected, match="task moved on"):
            await ledger.respond_interaction(
                question["interaction_id"], token=question["token"],
                response={"answer": "2025"}, owner_actor_id=OWNER,
            )
        assert (await repo.get_interaction(question["interaction_id"]))["status"] == "pending"
        assert str((await repo.get_task(task))["active_interaction_id"]) == question["interaction_id"]


async def test_resource_answer_as_sent_by_expert_screen(db):
    from app.application.workbench.interactions import answer_interaction
    from app.domain.workbench.states import AttemptState, TaskState
    from test_workbench_ledger_db import handover, seed

    _, _, sid = await seed(db)
    async with db() as session:
        repo = WorkbenchRepository(session)
        ledger = Ledger(repo)
        task = (await ledger.handover(handover(sid, budget="1"), owner_actor_id=OWNER))["task_id"]
        await ledger.transition(task, TaskState.VALIDATING)
        await ledger.transition(task, TaskState.QUEUED)
        step = await ledger.open_attempt(task, step_id="one", step_version="1")
        await ledger.attempt_transition(step["attempt_id"], AttemptState.RUNNING)
        await ledger.attempt_transition(step["attempt_id"], AttemptState.BUDGET_EXCEEDED, consumed=Decimal("1"))
        opened = next(e["payload"] for e in await repo.list_events(session_id=sid)
                      if e["type"] == "interaction/opened")
        reply = await answer_interaction(
            repo, opened["interaction_id"], token=opened["token"], response={"decision": "topup"},
            decision="topup", owner_actor_id=OWNER,
        )
        assert reply["state"] == TaskState.FAILED


async def test_answer_and_drive_enqueue_survive_separately(db, monkeypatch):
    from unittest.mock import AsyncMock
    from app.application.workbench.interactions import answer_interaction
    from app.domain.workbench.states import TaskState
    from test_workbench_ledger_db import handover, seed

    _, _, sid = await seed(db)
    async with db() as session:
        repo = WorkbenchRepository(session)
        ledger = Ledger(repo)
        task = (await ledger.handover(handover(sid), owner_actor_id=OWNER))["task_id"]
        await ledger.transition(task, TaskState.VALIDATING)
        question = await ledger.open_interaction(task, kind="input", waiting_reason=WaitingReason.INPUT,
            prompt=InteractionPrompt(title="资料", question="年度？"))
        monkeypatch.setattr(repo, "enqueue_command", AsyncMock(side_effect=RuntimeError("test queue outage")))
        with pytest.raises(RuntimeError, match="test queue outage"):
            await answer_interaction(repo, question["interaction_id"], token=question["token"],
                response={"answer": "2025"}, owner_actor_id=OWNER)
    async with db() as another_session:
        repo = WorkbenchRepository(another_session)
        assert (await repo.get_interaction(question["interaction_id"]))["status"] == "consumed"
        assert (await repo.get_task(task))["state"] == TaskState.QUEUED
        with pytest.raises(InteractionRejected):
            await answer_interaction(repo, question["interaction_id"], token=question["token"],
                response={"answer": "2025"}, owner_actor_id=OWNER)
