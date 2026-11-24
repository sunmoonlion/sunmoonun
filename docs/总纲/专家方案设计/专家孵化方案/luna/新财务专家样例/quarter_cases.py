"""Synthetic F2 cases. Produce prerequisite receipts with the pinned M02 algorithms."""

from calendar import monthrange
from copy import deepcopy
from datetime import date
from pathlib import Path
import sys

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "M02验收样表" / "工具实现")
)
from author_cases import fixtures
from reconcile import reconcile
from collect_checks import SLOTS, summarize


def period(q, parent_profit=None):
    month = q * 3
    end = date(2025, month, monthrange(2025, month)[1]).isoformat()
    version = f"合成甲2025Q{q}-原始版"
    checks = {}
    for name, tool in SLOTS:
        case = fixtures(tool)["cases"][0]["input"]["values"]
        target = {**case["target"], "结束日": end, "本期版本": version, "项目键": name}
        rows = deepcopy(case["rows"])
        for row in rows:
            if row["报告版本"] == "合成2025-v1":
                row["报告版本"] = version
            if row["截止日期"] == "2025-12-31":
                row["截止日期"] = end
            if name == "opening_balance":
                target["时点"] = "期初"
                row["截止日期"] = "2024-12-31"
                row["行名"] = row["行名"].replace("期末", "期初")
        if name == "profit" and parent_profit is not None:
            for row in rows:
                if row["行名"] == "净利润":
                    row["原始金额"] = str(parent_profit - 2)
                elif row["行名"] == "归属于母公司股东的净利润":
                    row["原始金额"] = str(parent_profit)
        checks[name] = reconcile(tool, target, rows)
    report = summarize(checks)
    assert report["阈值内"] == 5
    row = {
        **checks["profit"]["证据"][0],
        "行名": "营业收入",
        "证据编号": f"R{q}",
        "原始金额": str((40, 100, 190, 300)[q - 1]),
    }
    return row, report


def cases():
    rows = [period(q) for q in range(1, 5)]
    result = []

    def add(name, args, status, value):
        evidence = [args["current"]]
        if "previous" in args:
            evidence.append(args["previous"])
        assertions = {
            "/result/status": status,
            "/result/yuan": value,
            "/result/evidence": evidence,
        }
        result.append(
            {
                "case_id": name,
                "covers_promises": ["template_delivery"],
                "input": {"values": deepcopy(args)},
                "expected": {
                    "outcome": "succeeded",
                    "assertions": [
                        {"kind": "equals", "pointer": p, "value": v}
                        for p, v in assertions.items()
                    ],
                },
                "minimum_passes": 1,
                "repetitions": 1,
            }
        )

    for i, (row, report) in enumerate(rows):
        args = {"current": row, "current_checks": report}
        if i:
            prev, prior = rows[i - 1]
            args.update(
                previous=prev,
                previous_checks=prior,
                comparable_versions=[prev["报告版本"], row["报告版本"]],
            )
        add(f"q{i + 1}", args, "已还原", ("40", "60", "90", "110")[i])
    q2 = result[1]["input"]["values"]
    add(
        "missing_prior",
        {k: v for k, v in q2.items() if k not in ("previous", "previous_checks")},
        "缺相邻累计期",
        None,
    )
    add(
        "restated",
        {**q2, "comparable_versions": ["另一版", q2["current"]["报告版本"]]},
        "需确认可比版本链",
        None,
    )
    add(
        "wrong_scope",
        {**q2, "previous": {**q2["previous"], "范围": "母公司"}},
        "相邻累计期口径不符",
        None,
    )
    add(
        "earlier_receipt",
        {**q2, "previous_checks": q2["current_checks"]},
        "前期四式核验不足",
        None,
    )
    first = {"current": rows[0][0], "current_checks": rows[0][1]}
    add(
        "reported_balance",
        {
            **first,
            "current": {
                **first["current"],
                "表名": "资产负债表",
                "行名": "总资产",
                "起始日期": "",
                "原始金额": "830",
            },
        },
        "时点值",
        "830",
    )
    add(
        "missing_receipt",
        {
            "current": first["current"],
            "current_checks": {**first["current_checks"], "阈值内": 4},
        },
        "本期四式核验不足",
        None,
    )
    return result


if __name__ == "__main__":
    from quarter import calculate

    for case in cases():
        result = calculate(case["input"]["values"])
        for assertion in case["expected"]["assertions"]:
            assert result[assertion["pointer"].split("/")[-1]] == assertion["value"], (
                case["case_id"]
            )
    print(f"{len(cases())} F2 cases passed")
