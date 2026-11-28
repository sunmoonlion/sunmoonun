"""从冻结的 S01 v2 导出生成五要素修订稿。各回执沿用生产者的精确类型。"""

import argparse
import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from collect_scoped_checks import TOOLS


def prepare(frozen):
    draft = deepcopy(frozen["provenance"]["studio_draft"])
    procedure = draft["procedure"]
    source = deepcopy(frozen["provenance"]["source"])
    code = Path(__file__).with_name("collect_scoped_checks.py").read_bytes()
    assert frozen["version"] == 2 and set(procedure["inputs"]) == TOOLS.keys()
    source.update(version="2", digest="sha256:" + sha256(code).hexdigest())
    procedure["implementation"].update(
        version=source["version"], digest=source["digest"]
    )
    purpose = (
        "按委托项目清单汇集一至五项财报勾稽回执。可单独交付任意选中项目的原始回执，"
        "也可交付覆盖计数、明细与补件清单的报告。每项回执保留带符号差额和原行证据。"
    )
    draft.update(
        purpose=purpose,
        applies_when=[
            "委托已明确所选核验项和各项目键。回执可由上游核验工具产生。",
        ],
        excludes=["重新取数或重算财务公式。"],
    )
    procedure["instructions"] = purpose
    procedure["stop_conditions"] = ["拒绝越界回执、项目键不符和重复委托项。"]
    inputs = procedure["inputs"]
    scope_schema = {
        "type": "object",
        "minProperties": 1,
        "additionalProperties": False,
        "properties": {name: {"type": "string", "minLength": 1} for name in TOOLS},
    }
    inputs["scope"] = {
        "schema": scope_schema,
        "meaning": {"domain_id": "core.record.object"},
        "required": True,
        "on_missing": "fail",
        "description": "本次委托的核验项到项目键的映射。取自原委托，缺件仍保留该项。",
    }
    outputs = procedure["outputs"]
    report_schema = outputs["report"]["schema"]
    evidence_types = []
    for name in TOOLS:
        slot = inputs[name]
        slot.update(required=False, on_missing="omit")
        if slot["schema"] not in evidence_types:
            evidence_types.append(deepcopy(slot["schema"]))
        outputs[name] = deepcopy(slot)
        outputs[name]["description"] = "独立交付：" + slot["description"]
    missing = {
        "type": "object",
        "additionalProperties": False,
        "required": ["项目键", "状态", "差额元", "证据", "待补", "缺失回执"],
        "properties": {
            "项目键": {"type": "string"},
            "状态": {"const": "未核验"},
            "差额元": {"type": "null"},
            "证据": {"const": []},
            "待补": {"const": ["未收到核验回执"]},
            "缺失回执": {"enum": list(TOOLS)},
        },
    }
    report_schema["properties"]["明细"] = {
        "type": "array",
        "minItems": 1,
        "maxItems": len(TOOLS),
        "items": {"anyOf": [*evidence_types, missing]},
    }
    draft["expected_deliverables"][0].update(
        summary="按委托清单交付覆盖计数、回执明细及待补项目。",
        expected_schema=report_schema,
    )
    draft["validation_rules"][0]["check"] = (
        "应核数等于委托项目数；明细及计数包括缺件项。"
    )
    for name in TOOLS:
        label = inputs[name]["description"]
        draft["expected_deliverables"].append(
            {
                "promise_id": name,
                "summary": "独立交付：" + label,
                "expected_domain_id": "core.check.receipt",
                "expected_schema": outputs[name]["schema"],
                "delivery_mode": "conditional",
                "condition_input_hint": name,
                "condition_description": "该项在委托范围内，且实际收到该项回执。",
            }
        )
        draft["validation_rules"].append(
            {
                "promise_id": name,
                "outputs": [name],
                "on_failure": "fail",
                "check": "独立交付的回执逐字段等于该项输入，缺失时省略此端口。",
                "evidence": "逐端口用例比对回执全文，缺件用例检查汇总明细。",
            }
        )
    transfer = draft["access_ceiling"][0]["data_transfer"]
    transfer.update(
        argument_fields=list(inputs), purpose="在隔离容器内整理本次委托范围的回执。"
    )
    draft["approval_rules"][0].update(
        preview=list(inputs), when="执行前核对委托范围、回执与报价。"
    )
    return {"draft_contract": draft, "source": source, "allowed_callers": ["host"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frozen_version", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            prepare(json.loads(args.frozen_version.read_text())), ensure_ascii=False
        )
    )
