"""Compare the candidate gateway descriptor with ordinary conversation exposure."""

from contextlib import nullcontext
from types import SimpleNamespace as Node
from unittest.mock import AsyncMock

import pytest
from jsonschema import Draft202012Validator
from referencing.exceptions import Unresolvable

from app.application.workbench import formal_model_calls as probe
from app.application.workbench.formal_session_tools import method_input_schema
from app.domain.workbench.formal_method_generated import ValueSlot


@pytest.mark.asyncio
async def test_probe_and_conversation_expose_different_local_refs(monkeypatch):
    slot = ValueSlot.model_validate(
        {
            "description": "A local type",
            "required": True,
            "meaning": {},
            "on_missing": "fail",
            "schema": {"$defs": {"word": {"type": "string"}}, "$ref": "#/$defs/word"},
        }
    )
    procedure = Node(inputs={"message": slot})
    repo = Node(
        transaction=nullcontext,
        get_session=AsyncMock(return_value={"active_task_id": "task"}),
        get_task=AsyncMock(
            return_value={
                "id": "task",
                "active_attempt_id": "attempt",
                "pack_digest": "digest",
            }
        ),
        capability_selection=AsyncMock(return_value={"revision": 1}),
        capability_runtime=AsyncMock(),
    )
    service = probe.FormalModelCalls(
        Node(repo=repo, runtime_url="https://gateway.example.test")
    )
    context = Node(
        intent={"tool": {}, "source_asset_id": "asset"},
        registration=Node(service="local"),
        access={"operation_digest": "operation"},
        asset={"revision": 1},
    )
    monkeypatch.setattr(
        probe,
        "FormalHostCalls",
        lambda _: Node(context=AsyncMock(return_value=context)),
    )
    monkeypatch.setattr(probe, "snapshot_for_task", lambda _: Node(draft=None))
    monkeypatch.setattr(probe, "direct_procedure", lambda *args, **kwargs: procedure)
    monkeypatch.setattr(
        service, "scope", AsyncMock(return_value=(None, {"refs": {}}, None))
    )
    await service.prepare("owner", "session")
    runtime = repo.capability_runtime.await_args.args[-1]
    schema = runtime["tools"][probe.PROBE_TOOL]["tool"]["inputSchema"]
    assert Draft202012Validator(method_input_schema(procedure)).is_valid(
        {"message": "ok"}
    )
    with pytest.raises(Unresolvable):
        Draft202012Validator(schema).validate({"message": "ok"})
