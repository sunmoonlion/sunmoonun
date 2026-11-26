"""模型要求指标与原始年报页码时，两种资料进入同一条请求的现行行为。"""
from jsonschema import Draft202012Validator

from app.application.workbench.expert_data import _asked_need
from app.domain.workbench.platform_tools import TOOLS


def test_document_part_disappears_from_an_accepted_mixed_need():
    need = {
        "subject": "600519.SH",
        "metrics": ["IS.REVENUE"],
        "doc_type": "annual_report",
        "reading": "pages",
        "period": {"kind": "fixed", "start": "2025-01-01", "end": "2025-12-31"},
        "reason": "核对营收原数及原始年报页码",
    }
    schema = TOOLS["request_data"]["inputSchema"]
    Draft202012Validator(schema).validate({"task": "review", "needs": [need]})
    parsed = _asked_need(need, 1, 1).model_dump(mode="json")
    assert parsed["codes"] == ["IS.REVENUE"]
    assert "doc_type" not in parsed and "reading" not in parsed
