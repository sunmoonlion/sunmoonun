"""在 KnowLab 或 KnowBench 后端 app 目录以 PYTHONPATH=. 运行。"""
import importlib.util
from jsonschema import Draft202012Validator
from pydantic import ValidationError

if importlib.util.find_spec("app.domain.knowbots"):
    from app.domain.knowbots.formal_method import ValueSlot
else:
    from app.domain.workbench.formal_method_generated import ValueSlot

schema = {
    "$defs": {"number_or_text": {"anyOf": [{"type": "number"}, {"type": "string"}]}},
    "$ref": "#/$defs/number_or_text/anyOf/1",
}
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)
assert validator.is_valid("销售收入") and not validator.is_valid(42)
try:
    ValueSlot.model_validate({
        "description": "指标名称", "schema": schema, "meaning": {},
        "required": True, "on_missing": "fail",
    })
except ValidationError as error:
    assert "Method schema reference does not exist" in str(error)
else:
    raise AssertionError("此版本已经可以使用指向数组成员的本地引用")
