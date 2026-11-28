"""用同一份正式输出槽对照指令请求、步骤输出与脚本回执。"""
import base64
import hashlib
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from referencing.exceptions import Unresolvable

from app.application.workbench.instruction_turn import instruction_output
from app.domain.workbench.formal_execution import validate_values
from app.domain.workbench.formal_method_generated import ValueSlot
from app.domain.workbench.instruction_requests import instruction_job, leaf_responses_body
from app.domain.workbench.skill_execution import method_script_outputs


def test_reference_in_instruction_output_slot():
    slot = ValueSlot.model_validate({
        "description": "核验状态", "required": True, "meaning": {}, "on_missing": "fail",
        "schema": {"$defs": {"state": {"type": "string"}}, "$ref": "#/$defs/state"},
    })
    step = SimpleNamespace(instructions="返回状态", outputs={"status": slot})
    request = SimpleNamespace(draft=SimpleNamespace(definition=SimpleNamespace(procedure=step)))
    job = instruction_job(request, "核对", {})
    wire = leaf_responses_body(job, "example", 100)
    output = {"status": "通过"}
    assert validate_values(step.outputs, output) == output
    with pytest.raises(Unresolvable):
        Draft202012Validator(wire["text"]["format"]["schema"]).validate(output)


def test_repeated_field_in_instruction_and_script_output():
    raw = '{"report":{"passed":false,"passed":true}}'
    assert instruction_output([raw]) == {"report": {"passed": True}}
    data = raw.encode()
    receipt = {
        "exit_code": 0, "timed_out": False, "output_truncated": False, "stdout": "", "stderr": "",
        "artifacts": [{"path": "result.json", "sha256": hashlib.sha256(data).hexdigest(),
                       "data_base64": base64.b64encode(data).decode()}],
    }
    with pytest.raises(ValueError, match="duplicate"):
        method_script_outputs(receipt)
