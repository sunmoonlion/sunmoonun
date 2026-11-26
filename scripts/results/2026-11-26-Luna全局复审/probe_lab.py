"""Observe which promises require an explicit example at trial submission."""

from copy import deepcopy

import pytest
from pydantic import ValidationError
from tests.test_formal_method_execution import OWNER, prepared
from app.domain.knowbots.formal_method_execution import FormalMethodExecutionRequest


@pytest.mark.asyncio
async def test_unconditional_second_output_without_example():
    _, runtime, service, method_id, command = await prepared()
    await service.execute(OWNER, str(method_id), command)
    payload = runtime.submitted[command.run_id].model_dump(mode="json", by_alias=True)
    definition = payload["draft"]["definition"]
    declaration = definition["capability_declaration"]
    declaration["promises"]["evidence"] = "Return source evidence"
    outputs = definition["procedure"]["outputs"]
    outputs["evidence"] = deepcopy(outputs["result"])
    definition["how_to_validate"].append(
        {
            **definition["how_to_validate"][0],
            "promise_id": "evidence",
            "outputs": ["evidence"],
        }
    )
    accepted = FormalMethodExecutionRequest.model_validate(payload)
    (case,) = accepted.execution.suite.cases
    assert [rule.pointer for rule in case.expected.assertions] == ["/result"]
    assert not case.covers_promises
    declaration["conditions"] = {
        "evidence": {"when": "Data is present", "input_slots": ["value"]}
    }
    with pytest.raises(ValidationError, match="covering every promise"):
        FormalMethodExecutionRequest.model_validate(payload)
