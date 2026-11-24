"""Summarize the five approved M02 checks without recomputing their financial figures."""

import json
import os
from pathlib import Path

SLOTS = (
    ("opening_balance", "Q01"),
    ("closing_balance", "Q01"),
    ("profit", "Q02"),
    ("cash", "Q03"),
    ("inventory", "Q04"),
)


def summarize(arguments):
    rows = []
    keys = set()
    pending = []
    counts = {"阈值内": 0, "不平": 0, "未核验": 0}
    for name, tool in SLOTS:
        row = arguments[name]
        key = row["项目键"]
        status = row["状态"]
        if row["工具"] != tool or not key.strip() or key in keys:
            raise ValueError("核验回执的项目键重复或来源不符")
        if (row["差额元"] is None) != (status == "未核验"):
            raise ValueError("差额与核验状态不一致")
        keys.add(key)
        counts[status] += 1
        rows.append(row)
        if status == "未核验":
            if not row["待补"]:
                raise ValueError("未核验项必须说明待补资料")
            pending.append({"项目键": key, "待补": row["待补"]})
    return {
        "应核": len(rows),
        "实核": counts["阈值内"] + counts["不平"],
        **counts,
        "明细": rows,
        "待补清单": pending,
    }


if __name__ == "__main__":
    inputs = Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json"
    outputs = Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json"
    report = summarize(json.loads(inputs.read_text(encoding="utf-8")))
    outputs.write_text(json.dumps({"report": report}, ensure_ascii=False), encoding="utf-8")
