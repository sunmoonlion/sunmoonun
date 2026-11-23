import csv
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

M = Path(__file__).resolve().parents[1]
BASE = dict(
    主体="合成甲公司",
    范围="合并",
    开始日="2025-01-01",
    结束日="2025-12-31",
    本期版本="合成2025-v1",
)
with (M / "披露行.csv").open(encoding="utf-8") as stream:
    allrows = list(csv.DictReader(stream))
unique = {r["证据编号"]: r for r in allrows}
origin = {
    "Q01": ["B04", "B05", "B06"],
    "Q02": ["P01", "P02", "P03"],
    "Q03": ["C03", "C01", "C02"],
    "Q04": ["I01", "I02"],
}
unique["P03"] = {
    **unique["P02"],
    "证据编号": "P03",
    "行名": "少数股东损益",
    "原始金额": "-2.00",
}
labels = {
    "Q01": "A-L-E",
    "Q02": "NP-P-M",
    "Q03": "END-BEGIN-CHANGE",
    "Q04": "OPEN-PREV_CLOSE",
}
titles = {
    "Q01": "资产负债平衡核验",
    "Q02": "净利润归属核验",
    "Q03": "现金及现金等价物滚动核验",
    "Q04": "期初余额连续性核验",
}


def target(q):
    return {
        **BASE,
        "项目键": q + "-验收",
        **(
            {"时点": "期末"}
            if q == "Q01"
            else {"存量科目": "存货", "上期版本": "合成2024-v1"}
            if q == "Q04"
            else {}
        ),
    }


def fixed_id(q, what):
    return str(uuid5(NAMESPACE_URL, "sig-am/m02-author-20261123/" + q + "/" + what))


def fixtures(q):
    baseline = [dict(unique[k]) for k in origin[q]]
    expected = {
        "Q01": ("101.00", "1.00", "101.01", "1.01"),
        "Q02": ("8.00", "0.00", "6.99", "-1.01"),
        "Q03": ("43.00", "0.00", "45.00", "2.00"),
        "Q04": ("89.00", "-1.00", "88.00", "-2.00"),
    }[q]
    cases = []

    def add(case, rows, amount, ids, *, t=None):
        state = (
            "未核验"
            if amount is None
            else "不平"
            if abs(Decimal(amount)) > 1
            else "阈值内"
        )
        assertions = [
            {"kind": "equals", "pointer": "/check/" + k, "value": v}
            for k, v in [
                ("项目键", q + "-验收"),
                ("工具", q),
                ("算式", labels[q]),
                ("差额元", amount),
                ("状态", state),
            ]
        ]
        for i, key in enumerate(ids):
            assertions.append(
                {"kind": "equals", "pointer": f"/check/证据/{i}/证据编号", "value": key}
            )
        cases.append(
            {
                "case_id": case,
                "input": {"values": {"target": t or target(q), "rows": rows}},
                "repetitions": 1,
                "minimum_passes": 1,
                "expected": {"outcome": "succeeded", "assertions": assertions},
            }
        )

    baseline[0]["原始金额"] = expected[0]
    add("within", deepcopy(baseline), expected[1], origin[q])
    bad = deepcopy(baseline)
    bad[0]["原始金额"] = expected[2]
    add("difference", bad, expected[3], origin[q])
    add("missing", deepcopy(baseline[:-1]), None, origin[q][:-1])
    bad = deepcopy(baseline)
    if q == "Q01":
        bad[-1]["行名"] = "负债和所有者权益总计"
    elif q == "Q02":
        bad[-1]["范围"] = "母公司"
    elif q == "Q03":
        bad[0]["表名"] = "资产负债表"
        bad[0]["行名"] = "货币资金"
    else:
        bad[-1]["截止日期"] = "2025-12-31"
    add(
        "mismatch",
        bad,
        None,
        [
            k
            for i, k in enumerate(origin[q])
            if i != (0 if q == "Q03" else len(bad) - 1)
        ],
    )
    bad = deepcopy(baseline)
    bad[0].update(原单位="万元", 披露精度="1")
    add("precision", bad, None, origin[q])
    bad = deepcopy(baseline)
    bad.append(dict(bad[0]))
    add("duplicate", bad, expected[1], origin[q])
    if q == "Q04":
        bad = deepcopy(baseline)
        for row in bad:
            row.update(表名="利润表", 行名="累计营业收入")
        add("flow", bad, None, [], t={**target(q), "存量科目": "累计营业收入"})
    return {"suite_id": fixed_id(q, "suite"), "version": 1, "cases": cases}
