"""Characterize the reviewed baseline. Run with KnowBench's tests on PYTHONPATH."""

from unittest.mock import AsyncMock

import pytest
from formal_plan_support import setup_plan
from formal_recursive_support import register_completed
from test_ordinary_expert_execution_db import selected_match
from test_temporary_plan_db import receipt_proposal
from test_workbench_ledger_db import db as db

from app.application.workbench.formal_expert_intake import directory_for
from app.domain.workbench.errors import StaleStateVersion
from app.domain.workbench.formal_method_generated import CapabilityDeclaration

pytestmark = pytest.mark.asyncio


async def test_empty_directory_after_install(db, monkeypatch):
    ctx = await setup_plan(db)
    await register_completed(db, ctx)
    qualified = set()
    async with selected_match(
        db,
        monkeypatch,
        ctx.leaf,
        qualified,
        ctx.owner,
        ctx.factory,
        planning_choice=receipt_proposal(),
    ) as match:
        client, path, result, _, _, model = match
        review = {"review_digest": result["review_digest"]}
        endpoint = path + "/temporary-plan"
        first = await client.put(endpoint, json=review)
        assert first.status_code == 200
        assert first.json()["reason"] == "empty_catalog"
        assert first.json()["planning_task"] is None
        qualified.add(ctx.leaf.reference)
        replay = await client.put(endpoint, json=review)
        assert replay.json() == first.json()
        revised = await client.put(
            endpoint,
            json={**review, "clarification": "The receipt tool is now installed."},
        )
        assert revised.status_code == 409, revised.text
        assert not model.turn_inputs


async def test_unverifiable_handoff_then_correct_or_end(db, monkeypatch):
    ctx = await setup_plan(db)
    desk = AsyncMock()
    desk.submit.return_value = {"handoff": "new", "request_id": "missing-id"}
    async with selected_match(
        db,
        monkeypatch,
        ctx.leaf,
        set(),
        ctx.owner,
        ctx.factory,
        planning_choice=receipt_proposal(),
        incubations=desk,
    ) as match:
        client, path, result, *_ = match
        review = {"review_digest": result["review_digest"]}
        first = await client.put(
            path + "/handoff", json={**review, "gap": "Provide a cited report"}
        )
        changed = await client.put(
            path + "/handoff", json={**review, "gap": "Provide a cited table"}
        )
        ended = await client.put(path + "/end", json=review)
        assert [r.status_code for r in (first, changed, ended)] == [409, 409, 409]
        assert desk.submit.await_count == 1


async def test_large_declaration_hides_next_candidate():
    from uuid import uuid4
    from app.domain.workbench.formal_method_generated import MethodRef

    refs = [
        MethodRef(method_id=uuid4(), version=1, digest="sha256:" + "b" * 64)
        for _ in range(2)
    ]
    large = CapabilityDeclaration(
        title="报表核验",
        purpose="甲" * 12000,
        applies_when=["乙" * 12000],
        excludes=[],
        promises={"report": "报告"},
    )
    registry = AsyncMock()
    registry.planning_versions.return_value = {"items": refs, "next": None}
    registry.reference = lambda ref: ref.model_dump(mode="json")
    registry.planning_declaration.side_effect = [
        {"declaration": large.model_dump(mode="json")},
        {"title": "第二个候选"},
    ]
    with pytest.raises(StaleStateVersion, match="exceeds"):
        await directory_for(registry, "owner", "报表", None)
    assert registry.planning_declaration.await_count == 1
