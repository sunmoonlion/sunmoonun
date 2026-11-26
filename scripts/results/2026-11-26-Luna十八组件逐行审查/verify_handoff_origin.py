"""A formal handoff must identify a real UUID shape and describe a gap."""
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.domain.knowbots.method_demand import FormalHandoff
from tests.knowbot_fakes import OWNER
from tests.test_knowbot_incubation_service import Wired


@pytest.mark.asyncio
@pytest.mark.parametrize("field,value", [
    ("project_id", "-" * 36),
    ("task_id", "a" * 36),
    ("gap", "   "),
])
async def test_invalid_feedback_is_not_persisted(field, value):
    body = dict(
        contract="knowlab/formal-handoff/v1", owner_subject=OWNER,
        project_id=str(uuid4()), task_id=str(uuid4()), key="handoff-review",
        question="哪些行需要复核？", gap="对差额列出行号。",
        review_digest="sha256:" + "a" * 64,
    )
    body[field] = value
    wired = Wired()
    try:
        command = FormalHandoff.model_validate(body)
    except ValidationError:
        return
    await wired.svc.submit_from_runtime(OWNER, command, runtime="knowbench")
    assert not wired.repo.requests, f"invalid {field} persisted in an incubation request"
