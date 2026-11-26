"""Run with the KnowBench isolated PostgreSQL fixture and backend test imports."""

from uuid import uuid4
from decimal import Decimal
import pytest
from test_formal_script_execution_db import (
    Executor,
    script_setup,
    status,
    approve,
    collect_script,
    freeze,
    FormalMethodCatalog,
    FormalExecutions,
    WorkbenchRepository,
    OWNER,
)
from test_workbench_ledger_db import db as db
from app.domain.workbench.formal_method_execution_generated import (
    FormalTestSuiteDraft,
    FormalMethodExecutionRequest,
)
from app.domain.workbench.capabilities import CapabilityError


@pytest.mark.asyncio
async def test_passed_repetitions_cannot_resolve_when_failed_call_was_charged(db):
    class OnceFailed(Executor):
        async def start(self, owner, run, body):
            await super().start(owner, run, body)
            if len(self.calls) == 1:
                self.receipts[run] = {"state": "failed", "error": "fixture failure"}

    template, factory, conductor, executor = await script_setup(
        db, OnceFailed(), limit="3"
    )
    doc = template.model_dump(mode="json", by_alias=True)
    doc["run_id"] = str(uuid4())
    suite = doc["execution"]["suite"]
    suite.pop("digest")
    suite["suite_id"] = str(uuid4())
    suite["cases"][0]["repetitions"] = 2
    doc["execution"]["suite"] = (
        FormalTestSuiteDraft.model_validate(suite).freeze().model_dump(mode="json")
    )
    req = FormalMethodExecutionRequest.model_validate(doc)
    async with db() as s:
        repo = WorkbenchRepository(s)
        await FormalExecutions(repo, factory(repo)).accept(req, caller="knowlab")
    for _ in range(20):
        await conductor.advance(str(req.run_id))
        result = await status(db, req, factory)
        if result["status"] in ("passed", "failed"):
            break
        if result["actions"]:
            await approve(db, req, factory, result)
            await collect_script(db, factory)
    assert [case["outcome"] for case in result["cases"]] == ["failed", "succeeded"]
    assert Decimal(result["spent"]) == Decimal("0.08")
    assert result["status"] == "passed"
    frozen = freeze(req, result)
    async with db() as s:
        repo = WorkbenchRepository(s)
        svc = factory(repo)
        await svc.formal_sources.register(frozen, caller="knowlab")
        with pytest.raises(CapabilityError, match="reconcile"):
            await FormalMethodCatalog(
                repo, svc.formal_sources, svc.operations
            ).resolve_owned(OWNER, frozen.reference)
