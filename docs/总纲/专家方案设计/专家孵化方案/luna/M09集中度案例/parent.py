"""生成父专家的五要素工作稿；refs 来自目标作者的实际冻结版本。"""

import argparse
import json

from drafts import permission, tools


def contract(refs):
    steps = []
    for step_id, tool in (
        ("customers", "concentration"),
        ("suppliers", "concentration"),
        ("compare", "overlap"),
    ):
        _, purpose, inputs, output, result, _ = tools[tool]
        prior = {"customer": "customers", "supplier": "suppliers"}
        wires = {}
        for key, slot in inputs.items():
            binding = (
                {"source": "caller", "name": step_id}
                if tool == "concentration"
                else {"source": "step", "step": prior[key], "output": "receipt"}
            )
            wires[key] = {"slot": slot, "binding": binding}
        steps.append(
            {
                "id": step_id,
                "candidates": [refs[tool]],
                "select_when": purpose,
                "required_when": "每次交付",
                "always_required": True,
                "depends_on": [] if tool == "concentration" else list(prior.values()),
                "inputs": wires,
                "outputs": {output: result},
                "on_failure": "fail",
            }
        )
    result = tools["overlap"][4]
    return {
        "contract": "knowlab/method-draft/v2",
        "method_kind": "expert",
        "title": "前五大客户与供应商集中度透视",
        "purpose": "用客户和供应商披露排名交付销售、采购、已确认关联占比和有据交叉依存情况；风险评级待定",
        "applies_when": [
            "提供同一报告两张前五大排名表及对应总额，身份与关联标注均有出处"
        ],
        "excludes": ["跨期识别匿名主体、推定关联关系或给出风险等级"],
        "access_ceiling": [permission(tool) for tool in tools],
        "approval_rules": [
            {
                "requirement_id": tool,
                "operations": ["execute"],
                "when": "每次核对输入与报价",
                "preview": ["customers", "suppliers"],
                "on_denied": "pause",
            }
            for tool in tools
        ],
        "expected_deliverables": [
            {
                "promise_id": "report",
                "summary": "两侧集中度及交叉复核报告",
                "expected_domain_id": "core.record.object",
                "expected_schema": result["schema"],
            }
        ],
        "procedure": {
            "kind": "orchestration",
            "instructions": "分别核算两张表，再按有据身份对照并成稿",
            "max_steps": 3,
            "max_depth": 2,
            "max_expansions": 6,
            "max_replans": 0,
            "steps": steps,
            "exports": {
                "report": {
                    "step": "compare",
                    "output": "overlap",
                    "always_present": True,
                }
            },
        },
        "validation_rules": [
            {
                "promise_id": "report",
                "outputs": ["report"],
                "check": "逐项核对两侧独立分母、证据和评级待定",
                "evidence": "原行、注释及独立期望",
                "on_failure": "fail",
            }
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("references", type=argparse.FileType("r"))
    args = parser.parse_args()
    print(
        json.dumps(contract(json.load(args.references)), ensure_ascii=False, indent=2)
    )
