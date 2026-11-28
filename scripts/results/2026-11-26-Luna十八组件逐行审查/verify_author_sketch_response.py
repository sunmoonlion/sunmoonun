"""Validate the actual author projection against the provider's published model shape."""
from datetime import UTC, datetime
from uuid import uuid4

from jsonschema import Draft202012Validator
from app.application.ports.knowbots import IncubationRecord
from app.domain.knowbots.selection import Selection
from app.interfaces.endpoints.knowbot_views import incubation_view


def test_author_receives_the_same_selection_shape_that_was_reviewed():
    proposal = Selection.model_validate({
        "status": "clarify", "reason": "Which period?", "steps": [], "routing_required": False
    }).model_dump(mode="json")
    validator = Draft202012Validator(Selection.model_json_schema())
    validator.validate(proposal)
    record = IncubationRecord(
        id=uuid4(), request_id=uuid4(), workdraft_id=uuid4(), owner_subject="author",
        round=1, action="draft", status="succeeded", run_id="example", budget_limit="1",
        timeout_seconds=60, environment_id="computer", workspace_root="/workspace",
        request_version=1, started_at=datetime.now(UTC),
        seed={"selection_context": {"partial": False, "methods": {}, "patterns": {}}},
        handback={"selection": proposal},
    )
    validator.validate(incubation_view(record, [])["selection"])
