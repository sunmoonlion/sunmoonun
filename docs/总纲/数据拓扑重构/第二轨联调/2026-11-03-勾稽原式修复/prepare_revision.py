"""Build an author-owned revision; no DB writes, deployment or model calls.

The owner requested repair of substituted reconciliation formulas on 2026-11-03.
Financial formulas remain expert content, compiled by the existing generic engine.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

FORMULAS = {
    "balance": ("A-(L+E)", ["A", "L", "E"], "资产总计、负债合计、所有者权益合计"),
    "profit": ("NP-(P+M)", ["NP", "P", "M"], "净利润、归母净利润、少数股东损益"),
    "cash": (
        "END-(BEGIN+CHANGE)",
        ["END", "BEGIN", "CHANGE"],
        "期末现金、期初现金、现金净增加额",
    ),
    "continuity": (
        "OPEN-PREV_CLOSE",
        ["OPEN", "PREV_CLOSE"],
        "本期期初、上期期末（同一科目口径）",
    ),
}


def sha(value):
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


def table(name, fields):
    return {
        "name": name,
        "type": "table",
        "items": [{"name": k, "type": t} for k, t in fields.items()],
    }


def check(template, **params):
    return {"template": template, "params": params}


def prepare(before):
    body = copy.deepcopy(before["body"])
    steps = {s["id"]: s for s in body["steps"]}
    inventory, reconcile, series, forecast = (
        steps[k] for k in ["inventory", "reconcile", "series", "forecast"]
    )
    # Preserve original author text and narrative outputs for existing consumers.
    inventory["rules"].append(
        {
            "id": "reconciliation_scope",
            "text": "按本题历史分析、单季换算、回测和预测所需的期间列出四类待核清单：balance_plan、profit_plan、cash_plan、continuity_plan。"
            "每项只交回 key；key 要包含期间、报表口径、来源材料版本，衔接检查还含科目及前后期。只列需要核验的实际范围，不机械扩展到无关科目。"
            "同一事实同一版本不因重复披露重复列项；不同重述版分开。需要核验但缺输入的项目也要列出，不能为验收删掉。每类至少一项。",
        }
    )
    for kind in FORMULAS:
        plan = f"{kind}_plan"
        inventory["outputs"].append(table(plan, {"key": "text"}))
        inventory["checks"] += [
            check("list_min", path=plan),
            check(
                "each_has",
                path=plan,
                keys=["key"],
                non_empty_keys=["key"],
                unique_by=["key"],
            ),
        ]
    reconcile["rules"].append(
        {
            "id": "original_formula_records",
            "text": "原四条恒等式及1元阈值不变。按inventory的四类清单逐项核验，key逐字照抄。"
            "balance_checks用A-(L+E)，profit_checks用NP-(P+M)，cash_checks用END-(BEGIN+CHANGE)，continuity_checks用OPEN-PREV_CLOSE。"
            "每项交回原始compute_id、value（实际差额，元，不作展示四舍五入）和公式各输入的实际值。"
            "A为资产总计，L为负债合计，E为所有者权益合计；NP为净利润，P为归母净利润，M为少数股东损益；END/BEGIN/CHANGE为现金流量表期末/期初/净增加额；OPEN/PREV_CLOSE为同一科目的本期期初/上期期末。"
            "计算输入必须来自对应期间、口径、版本的事实或已核原文证据，不准以资产减负债反推权益再代入同一式，不准用同一事实自减凑零。"
            "资产总计与负债和权益总计对照仅是辅助，不可放入这四类原式记录，不能宣布原式通过。"
            "差额绝对值<=1元的项目平衡；>1元的项目不平，保留实际差额及局限并按原方法继续，不平期不得进入预测。"
            "缺输入先按既有工具查询事实、定位原文和补数据流程处理；仍不能计算的放对应balance_missing/profit_missing/cash_missing/continuity_missing，写key与reason，不编compute_id或0。"
            "已计算和缺项两类合起来必须逐项覆盖清单，不遗漏、不重复；缺项是未核验，不能记作通过，也不能把辅助对照描述为四式全通过。"
            "checks保留文字摘要，必须与这八张结构化表一致；未核验与不平分别写明，不能统称全部通过。",
        }
    )
    for kind, (expression, inputs, _) in FORMULAS.items():
        done, missing = f"{kind}_checks", f"{kind}_missing"
        reconcile["outputs"] += [
            table(done, {"key": "text", **{x: "number" for x in inputs}}),
            table(missing, {"key": "text", "reason": "text"}),
        ]
        reconcile["checks"] += [
            check(
                "each_has",
                path=done,
                keys=["key", "value", "compute_id", *inputs],
                non_empty_keys=["key", "compute_id"],
                unique_by=["key"],
            ),
            check(
                "computed",
                path=done,
                expression=expression,
                tolerance=0.0,
                input_keys=inputs,
            ),
            check(
                "each_has",
                path=missing,
                keys=["key", "reason"],
                non_empty_keys=["key", "reason"],
                unique_by=["key"],
            ),
            check(
                "covers",
                path=done,
                field="key",
                source_step="inventory",
                source_path=f"{kind}_plan",
                source_field="key",
                also=[missing],
            ),
        ]
    series["rules"].append(
        {
            "id": "reconciliation_evidence",
            "text": "以上游reconcile四类*_checks的真实差额及*_missing为核验依据，不只读checks文字摘要。"
            "缺项未核验不等于不平，更不等于已通过；不能以辅助总计对照补足原四式。"
            "不平期继续按原方法剔出预测；未核验期必须明确标注并按既有补数据流程处理，不能包装成已核验数据。保留原季度换算方法与报告版本一致性。",
        }
    )
    if "reconcile" not in forecast["uses"]:
        forecast["uses"].append("reconcile")
    forecast["rules"].append(
        {
            "id": "reconciliation_gate",
            "text": "直接查看reconcile四类计算表及缺项表。预测所用期间必须有原式证据，辅助总计对照不能替代；缺项不得宣称核验通过。"
            "若预测、回测所需数据仍缺原式核验，按既有补数据流程处理，如实说明尚不能交付的部分；不缩短原回测与同比窗口，不编预测数。"
            "本条只落实上游原式证据要求，不改变季节性同比算法、两季预测、最近四季回测或1元阈值。",
        }
    )
    # Structured reconciliation has more evidence than the former prose list.
    for sid in ["reconcile", "series", "forecast", "writeup"]:
        steps[sid]["advanced"]["input_max_chars"] = max(
            40000, steps[sid]["advanced"].get("input_max_chars") or 0
        )
    edits = []
    old = {s["id"]: s for s in before["body"]["steps"]}
    for sid, step in steps.items():
        for field in ["outputs", "checks", "rules", "uses"]:
            if old[sid][field] != step[field]:
                edits.append([f"steps/{sid}/{field}", step[field]])
        if old[sid]["advanced"] != step["advanced"]:
            edits.append([f"steps/{sid}/advanced", step["advanced"]])
    return {
        "status": "owner_requested_repair_not_yet_published",
        "base_revision": before["revision"],
        "base_body_sha256": sha(before["body"]),
        "body": body,
        "edits": edits,
        "unchanged": [
            "scope",
            "indicators",
            "official",
            "test_cases",
            "test_set",
            "budget",
            "original_four_formulas",
            "one_yuan_threshold",
            "forecast_algorithm",
        ],
        "limitations": [
            "Formula, value, operands and planned-item coverage are deterministic; source semantics and narrative consistency still require review.",
            "Missing source facts need the existing authorized supply/revision flow; this script does not write data or restart tests.",
        ],
    }


if __name__ == "__main__":
    print(
        json.dumps(
            prepare(json.loads(Path(sys.argv[1]).read_text())),
            ensure_ascii=False,
            indent=2,
        )
    )
