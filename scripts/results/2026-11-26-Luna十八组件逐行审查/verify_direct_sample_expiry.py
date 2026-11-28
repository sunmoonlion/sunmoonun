"""以同一冻结版本比较临时数据过期前后的自用送审材料。"""
from datetime import UTC, datetime, timedelta

import pytest
from formal_method_use_support import admitted
from test_workbench_ledger_db import db

from app.application.workbench.test_runs import KnowbotTestConductor
from app.bootstrap.workbench import workbench_stores
from app.infrastructure.workbench.repository import WorkbenchRepository


@pytest.mark.asyncio
async def test_registered_direct_method_loses_self_review_sample(db):
    frozen, _, _, factory, _ = await admitted(db)
    async with db() as session:
        repo = WorkbenchRepository(session)
        service = factory(repo).formal_sources
        before = await service.self_review_outputs("author", frozen.reference)
        assert before["samples"] == [{"steps": [{"artifact": {"receipt": "expected-never-sent"}}]}]
        future = datetime.now(UTC) + timedelta(days=31)
        await KnowbotTestConductor(workbench_stores(db), now=lambda: future).cleanup()
        assert await service.self_review_outputs("author", frozen.reference) == {
            **before, "samples": []
        }
        assert (await service.registration(
            "author", str(frozen.reference.method_id), frozen.reference.version, caller="knowlab"
        ))["status"] == "registered"
