"""S01 按委托清单汇总。单项输出使用固定端口名，专家可在编排中另取交付名。"""

import json
import os
from pathlib import Path

TOOLS = {
    "opening_balance": "Q01",
    "closing_balance": "Q01",
    "profit": "Q02",
    "cash": "Q03",
    "inventory": "Q04",
}


def collect(arguments):
    scope = arguments["scope"]
    if not isinstance(scope, dict) or not scope or scope.keys() - TOOLS.keys():
        raise ValueError("委托清单须选择至少一项已登记的核验")
    if any(not isinstance(key, str) or not key.strip() for key in scope.values()):
        raise ValueError("委托项目键不能为空")
    if len(set(scope.values())) != len(scope):
        raise ValueError("委托项目键重复")
    if arguments.keys() - {"scope"} - scope.keys():
        raise ValueError("收到委托范围外的回执")

    counts = {"阈值内": 0, "不平": 0, "未核验": 0}
    outputs = {}
    details = []
    pending = []
    for slot, tool in TOOLS.items():
        if slot not in scope:
            continue
        key = scope[slot]
        if slot in arguments:
            row = arguments[slot]
            if row["工具"] != tool or row["项目键"] != key:
                raise ValueError("回执来源或项目键与本次委托不符")
            status = row["状态"]
            if status not in counts or (row["差额元"] is None) != (status == "未核验"):
                raise ValueError("差额与核验状态不一致")
            if status == "未核验" and not row["待补"]:
                raise ValueError("未核验回执须说明待补资料")
            outputs[slot] = row
        else:
            row = {
                "项目键": key,
                "状态": "未核验",
                "差额元": None,
                "证据": [],
                "待补": ["未收到核验回执"],
                "缺失回执": slot,
            }
        details.append(row)
        counts[row["状态"]] += 1
        if row["状态"] == "未核验":
            pending.append({"项目键": key, "待补": row["待补"]})

    outputs["report"] = {
        "应核": len(scope),
        "实核": len(scope) - counts["未核验"],
        **counts,
        "明细": details,
        "待补清单": pending,
    }
    return outputs


if __name__ == "__main__":
    inputs = Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json"
    outputs = Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json"
    outputs.write_text(
        json.dumps(
            collect(json.loads(inputs.read_text(encoding="utf-8"))), ensure_ascii=False
        ),
        encoding="utf-8",
    )
