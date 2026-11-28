"""Observe the same completed model turn in the collector and catalog verifier."""

from types import SimpleNamespace
import pytest
from test_formal_model_evidence import facts, collect
from app.application.workbench.formal_method_catalog import _verify_model_case
from app.domain.workbench.formal_execution import snapshot_for_task
from app.domain.workbench.capabilities import CapabilityError


@pytest.mark.asyncio
async def test_usage_delivered_after_completion_is_classified_differently():
    world = facts()
    usage = next(
        event for event in world.events if event["type"] == "thread/tokenUsage/updated"
    )
    usage["cursor"] = max(event["cursor"] for event in world.events) + 1
    world.events.sort(key=lambda event: event["cursor"])
    proof = await collect(world)
    assert proof["validated"], proof["errors"]
    item = {
        "model_provenance": proof,
        "model_turn_ids": ["turn"],
        "snapshot_digest": world.task["pack_digest"],
    }
    result = SimpleNamespace(
        attempt_id=world.attempt["id"],
        model_trace=SimpleNamespace(**world.result["model_trace"]),
    )
    with pytest.raises(CapabilityError, match="usage was not priced"):
        _verify_model_case(
            world.request, snapshot_for_task(world.task), item, result, set()
        )
