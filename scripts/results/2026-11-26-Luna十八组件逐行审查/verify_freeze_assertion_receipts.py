"""Check how author-side freeze handles contradictory per-assertion evidence."""
import pytest

from app.application.errors.exceptions import AppException
from app.domain.knowbots.formal_method_admission import FreezeFormalMethod
from tests.test_formal_method_execution import OWNER, complete_trial, prepared


@pytest.mark.parametrize("assertions", [
    [],
    [{"index": 0, "passed": False, "detail": "different value"}],
    [{"index": 1, "passed": True, "detail": "unrequested assertion"}],
])
async def test_freeze_requires_evidence_for_the_frozen_assertion(assertions):
    _, runtime, service, method, command = await prepared()
    await service.execute(OWNER, str(method), command)
    _, report = complete_trial(runtime, command, business=False)
    report["cases"][0]["assertions"] = assertions
    with pytest.raises(AppException):
        await service.freeze(
            OWNER, str(method), 1, FreezeFormalMethod(
                request_id=command.request_id, revision=2, run_id=command.run_id,
                visibility="private",
            )
        )


async def test_poll_binds_suite_to_the_requested_run():
    from uuid import uuid4
    from app.domain.knowbots.formal_method_execution import ExecuteFormalMethod

    _, runtime, service, method, first = await prepared()
    await service.execute(OWNER, str(method), first)
    updated = first.model_dump(mode="json")
    updated["run_id"] = str(uuid4())
    updated["execution"]["suite"]["version"] += 1
    updated["execution"]["suite"]["cases"][0]["input"]["values"]["value"] = 9
    second = ExecuteFormalMethod.model_validate(updated)
    reply = await service.execute(OWNER, str(method), second)
    runtime.executions[first.run_id]["suite"] = reply["suite"]
    with pytest.raises(AppException):
        await service.execution(OWNER, str(method), str(first.request_id), str(first.run_id))
