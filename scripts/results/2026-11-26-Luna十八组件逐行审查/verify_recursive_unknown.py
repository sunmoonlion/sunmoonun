"""Read the provider, step, and subtree receipts for one interrupted external response."""

from formal_plan_support import advance
from formal_recursive_support import setup_recursive
from test_formal_execution_db import approve
from test_workbench_ledger_db import db as db

from app.application.workbench.delegation_receipts import handoffs
from app.infrastructure.workbench.repository import WorkbenchRepository


async def test_unknown_receipts(db):
    ctx = await setup_recursive(db)
    pending = await advance(db, ctx)
    task_id = pending["cases"][0]["task_id"]

    async def interrupted(*args):
        raise TimeoutError("synthetic lost response")

    ctx.remote.call = interrupted
    await approve(db, ctx.request, ctx.factory, pending)
    final = await advance(db, ctx)
    assert final["status"] == "failed"
    async with db() as session:
        repo = WorkbenchRepository(session)
        [attempt] = await repo.list_attempts(task_id)
        refs = attempt["refs"]
        operation = await repo.capability_call(ctx.owner, refs["capability_call_id"])
        assert operation["status"] == "unknown"
        assert operation["detail"]["result"]["message"]
        assert refs["formal_result"]["outcome"] == "unknown"
        assert refs["formal_result"]["detail"] == ""
        view = await handoffs(repo, ctx.owner, task_id)
        receipts = [
            receipt
            for parent in view["parents"]
            for child in parent["children"]
            for entry in child["rounds"]
            for receipt in entry["receipts"]
            if receipt["attempt_id"] is None
        ]
        assert any(r["state"] == "FAILED" and not r["failure"] for r in receipts)
