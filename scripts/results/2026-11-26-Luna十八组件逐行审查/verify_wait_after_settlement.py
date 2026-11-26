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
