"""Use a disposable DB and a backdated ordinary question."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from test_workbench_ledger_db import OWNER, db as db, seed
from app.application.workbench.runner import SandboxLink
from app.infrastructure.workbench.repository import (
    SqlWorkbenchStores,
    WorkbenchRepository,
)


async def test_expired_question_on_session_and_owner_lists(db):
    _, _, sid = await seed(db)
    token = "fixture-for-expired-question"
    async with db() as session:
        repo = WorkbenchRepository(session)
        async with repo.transaction():
            iid = await repo.insert_interaction(
                session_id=sid,
                task_id=None,
                attempt_id=None,
                kind="question",
                prompt={"subject": {"request_id": "ordinary"}},
                subject_digest=None,
                token=token,
                target_state_version=None,
                expires_at=datetime.now(UTC) - timedelta(seconds=1),
            )
    link = SandboxLink(
        SimpleNamespace(stores=SqlWorkbenchStores(db)), {"id": "fixture"}
    )
    await link._settle_timeout(
        session={"owner_actor_id": OWNER},
        where={},
        opened={"interaction_id": iid, "token": token},
    )
    async with db() as session:
        repo = WorkbenchRepository(session)
        assert (await repo.get_interaction(iid))["status"] == "pending"
        assert len(await repo.list_interactions(session_id=sid, status="pending")) == 1
        assert not await repo.list_owner_interactions(
            owner_actor_id=OWNER, status="pending"
        )
