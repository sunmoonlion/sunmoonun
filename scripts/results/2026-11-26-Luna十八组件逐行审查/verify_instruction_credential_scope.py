"""同一作者的两台测试电脑各持一路由相同的凭据，不连接供应方。"""
import pytest
from test_instruction_requests_db import OWNER, PRICES, ROUTE, setup
from test_workbench_ledger_db import db, seed

from app.application.workbench.instruction_requests import InstructionRequests
from app.domain.workbench.capabilities import CapabilityError


@pytest.mark.asyncio
async def test_newer_other_sandbox_credential_shadows_working_route(db):
    host, task_id, original, _ = await setup(db)
    _, second_sandbox, _ = await seed(db, root="/home/u/research/second")
    async with host() as base:
        repo = base.repo
        task = await repo.get_task(task_id)
        session = await repo.get_session(str(task["session_id"]), owner_actor_id=OWNER)
        assert str(session["sandbox_id"]) != str(second_sandbox)

        async def choose():
            return await InstructionRequests.for_account(
                base.formal, OWNER, routes=[ROUTE], model=ROUTE.model, prices=PRICES, default_url=""
            )

        eligible = await choose()
        assert (await eligible.account_quote(OWNER, session, "CNY"))["credential_id"] == str(original["id"])
        async with repo.transaction():
            newer = await repo.add_credential(
                owner_actor_id=OWNER, provider=ROUTE.provider, sandbox_id=second_sandbox,
                ciphertext="fixture", hint="test", base_url=ROUTE.base_url,
            )
        selected = await choose()
        assert selected.credential_id == str(newer["id"])
        with pytest.raises(CapabilityError, match="No active credential"):
            await selected.account_quote(OWNER, session, "CNY")
        assert (await eligible.account_quote(OWNER, session, "CNY"))["credential_id"] == str(original["id"])
