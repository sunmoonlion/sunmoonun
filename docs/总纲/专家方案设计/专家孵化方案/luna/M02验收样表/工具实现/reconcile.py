"""M02 author implementation. Each registered entry fixes its own Q identifier."""

from datetime import date, timedelta
from decimal import Decimal, localcontext
import re


UNITS = {"元": 1, "千元": 1000, "万元": 10000, "亿元": 100000000}
MONEY = re.compile(r"-?(?:0|[1-9][0-9]{0,23})(?:\.[0-9]{1,12})?\Z")
FORMULAS = {
    "Q01": "A-L-E",
    "Q02": "NP-P-M",
    "Q03": "END-BEGIN-CHANGE",
    "Q04": "OPEN-PREV_CLOSE",
}


def operands(kind, target):
    start = target["开始日"]
    end = target["结束日"]
    opening = (date.fromisoformat(start) - timedelta(days=1)).isoformat()
    if date.fromisoformat(end) < date.fromisoformat(start):
        raise ValueError("报告期间无效")
    version = target["本期版本"]
    if kind == "Q01":
        position = target["时点"]
        day = {"期初": opening, "期末": end}[position]
        return [
            ("资产负债表", position + line, "", day, version)
            for line in ("资产总计", "负债合计", "所有者权益合计")
        ]
    if kind == "Q02":
        return [
            ("利润表", line, start, end, version)
            for line in ("净利润", "归属于母公司股东的净利润", "少数股东损益")
        ]
    if kind == "Q03":
        return [
            ("现金流量表", "期末现金及现金等价物余额", "", end, version),
            ("现金流量表", "期初现金及现金等价物余额", "", opening, version),
            ("现金流量表", "现金及现金等价物净增加额", start, end, version),
        ]
    if kind != "Q04":
        raise ValueError("未知核验方法")
    account = target["存量科目"]
    previous = target["上期版本"]
    if not account.strip() or not previous.strip() or previous == version:
        raise ValueError("连续性核对需要科目和两个独立报告版本")
    return [
        ("资产负债表", "期初" + account, "", opening, version),
        ("资产负债表", "期末" + account, "", opening, previous),
    ]


def reconcile(kind, target, rows):
    """A single declared check over already supplied, source-labelled rows."""
    expected = operands(kind, target)
    evidence = []
    missing = []
    values = []
    for table, line, start, end, version in expected:
        matches = []
        for row in rows:
            if (
                row["表名"],
                row["行名"],
                row["起始日期"],
                row["截止日期"],
                row["报告版本"],
                row["主体"],
                row["范围"],
            ) != (table, line, start, end, version, target["主体"], target["范围"]):
                continue
            if row not in matches:
                matches.append(row)
        evidence.extend(matches)
        if len(matches) != 1:
            missing.append(f"{version} {table} {line}：需一条口径一致且可定位的披露")
            continue
        row = matches[0]
        if not row["证据编号"].strip() or not row["页"].strip():
            missing.append(line + "：需原表位置")
            continue
        if any(other != row and other["证据编号"] == row["证据编号"] for other in rows):
            missing.append(line + "：证据编号指向多条记录")
            continue
        if kind == "Q02" and target["范围"] != "合并":
            missing.append(line + "：需合并利润归属口径")
            continue
        unit = UNITS.get(row["原单位"])
        if row["币种"] != "CNY" or unit is None:
            missing.append(line + "：需人民币与明确披露单位")
            continue
        raw, quantum = row["原始金额"], row["披露精度"]
        if not MONEY.fullmatch(raw) or not MONEY.fullmatch(quantum):
            missing.append(line + "：需披露的十进制金额及精度")
            continue
        with localcontext() as ctx:
            ctx.prec = 64
            resolution = Decimal(quantum)
            if resolution <= 0 or resolution * unit > 1 or Decimal(raw) % resolution:
                missing.append(line + "：需足以核对 1 元阈值的原始披露精度")
                continue
            values.append(Decimal(raw) * unit)
    difference = None
    if not missing:
        with localcontext() as ctx:
            ctx.prec = 64
            difference = values[0] - sum(values[1:])
    return {
        "项目键": target["项目键"],
        "工具": kind,
        "算式": FORMULAS[kind],
        "证据": evidence,
        "差额元": None if difference is None else format(difference, "f"),
        "状态": "未核验" if missing else ("不平" if abs(difference) > 1 else "阈值内"),
        "待补": missing,
    }
