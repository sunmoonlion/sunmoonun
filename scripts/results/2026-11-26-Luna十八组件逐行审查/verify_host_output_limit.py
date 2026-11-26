"""用宿主入口跑一次大输出，核对用例、任务与最终封存的结论。"""
import pytest
from test_formal_execution_db import StructuredRemote, approve, setup, settle, status
from test_workbench_ledger_db import db

from app.infrastructure.workbench.repository import WorkbenchRepository


class LargeReceipt(StructuredRemote):
    async def call(self, *args):
        result = await super().call(*args)
        result["structuredContent"]["receipt"] = "a" * 64001
        return result


@pytest.mark.asyncio
async def test_host_reports_success_before_size_check(db):
    case = {
        "case_id": "large",
        "input": {"values": {"to": "test@example.test"}},
        "repetitions": 1,
        "minimum_passes": 1,
        "expected": {
            "outcome": "succeeded",
            "assertions": [{"kind": "contains", "pointer": "/receipt", "value": "aaa"}],
        },
    }
    req, _, _, factory, conductor = await setup(db, remote=LargeReceipt(), cases=[case])
    await conductor.advance(str(req.run_id))
    await approve(db, req, factory, await status(db, req, factory))
    await settle(conductor, req)
    final = await status(db, req, factory)
    result = final["cases"][0]
    assert result["status"] == "passed" and result["outcome"] == "succeeded"
    assert final["status"] == "failed"
    async with db() as session:
        repo = WorkbenchRepository(session)
        assert (await repo.get_task(result["task_id"]))["state"] == "SUCCEEDED"
        attempt = await repo.get_attempt(result["attempt_id"])
        assert len(attempt["refs"]["formal_result"]["outputs"]["receipt"]) == 64001
