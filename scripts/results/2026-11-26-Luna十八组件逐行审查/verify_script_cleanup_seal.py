"""隔离数据库核对脚本已成功但环境释放迟到时的正式试跑结论。"""
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from test_formal_execution_db import approve, settle, status
from test_formal_script_execution_db import Executor, script_setup
from test_workbench_ledger_db import db

from app.infrastructure.workbench.repository import WorkbenchRepository
from test_capabilities_db import OWNER


@pytest.mark.asyncio
async def test_successful_script_with_delayed_cleanup(db):
    executor = Executor()
    executor.cancel = AsyncMock(side_effect=[TimeoutError(), None])
    req, factory, conductor, _ = await script_setup(db, executor)
    await conductor.advance(str(req.run_id))
    pending = await status(db, req, factory)
    cid = pending["actions"][0]["call_id"]
    await approve(db, req, factory, pending)
    async with db() as session:
        repo = WorkbenchRepository(session)
        await factory(repo).reconcile_scripts()
        call = await repo.capability_call(OWNER, cid)
        assert call["status"] == "succeeded" and call["detail"]["script_cleanup_pending"]
        assert (await repo.script_budget_entries(cid))["consume"]["amount"] == Decimal("0.04")
    await settle(conductor, req)
    result = await status(db, req, factory)
    assert result["cases"][0]["status"] == "passed"
    assert result["status"] == "failed"
    async with db() as session:
        repo = WorkbenchRepository(session)
        evidence = (await repo.formal_validation(OWNER, str(req.run_id)))["execution_evidence"]
        assert evidence["cases"][0]["errors"] == ["call_digest_mismatch"]
        await factory(repo).reconcile_scripts()
        assert not await repo.pending_metered_scripts()
    assert (await status(db, req, factory))["status"] == "failed"
