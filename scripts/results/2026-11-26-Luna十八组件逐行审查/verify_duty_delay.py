"""A prior wake error races a committed pause followed by resume of the same period."""
from datetime import datetime, timedelta, timezone
from test_workbench_ledger_db import OWNER, db as db, handover, seed
from app.application.workbench.ledger import Ledger
from app.infrastructure.workbench.repository import WorkbenchRepository


async def test_stale_error_after_resume(db):
    _, _, sid = await seed(db)
    period = datetime.now(timezone.utc)
    async with db() as session:
        repo = WorkbenchRepository(session)
        origin = (await Ledger(repo).handover(handover(sid), owner_actor_id=OWNER))["task_id"]
        async with repo.transaction():
            await repo.create_duty(origin, {}, period)
            await repo.approve_duty_output(origin, {"sample": True})
        observed, = await repo.due_duties(period)
        before = await repo.duty(origin)
        for paused in (True, False):
            async with repo.transaction():
                await repo.pause_duty(origin, paused)
        resumed = await repo.duty(origin)
        assert resumed["state_revision"] != before["state_revision"]
        assert resumed["problem"] is None and not resumed["paused"]
        async with repo.transaction():
            await repo.delay_duty(origin, observed["next_at"], period + timedelta(minutes=5),
                                  "prior_attempt_failed")
        assert (await repo.duty(origin))["problem"] == "prior_attempt_failed"
        assert not await repo.due_duties(period)
