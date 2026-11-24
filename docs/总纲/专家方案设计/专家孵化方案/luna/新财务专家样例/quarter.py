"""F2 author tool for a calendar-year CNY disclosure. Amounts are in yuan."""

from calendar import monthrange
from datetime import date
from decimal import Decimal, localcontext
import json
import os
from pathlib import Path
import re

UNITS = {"元": 1, "千元": 1000, "万元": 10000, "亿元": 100000000}
AMOUNT = re.compile(r"-?(?:0|[1-9][0-9]{0,23})(?:\.[0-9]{1,12})?")


def verified(row, report):
    if not report or report["应核"] != 5 or report["阈值内"] != 5:
        return False
    details = report["明细"]
    if [c["工具"] for c in details] != ["Q01", "Q01", "Q02", "Q03", "Q04"]:
        return False
    for check in details:
        if check["状态"] != "阈值内" or not check["证据"] or check["待补"]:
            return False
        if any(
            (e["主体"], e["范围"]) != (row["主体"], row["范围"]) for e in check["证据"]
        ):
            return False
    end = row["截止日期"]
    start = end[:4] + "-01-01"
    opening = f"{int(end[:4]) - 1}-12-31"
    # Four identities over this exact report; continuity also cites the prior report.
    version = row["报告版本"]
    dates = [
        [opening] * 3,
        [end] * 3,
        [end] * 3,
        [end, opening, end],
        [opening, opening],
    ]
    for idx, (check, expected) in enumerate(zip(details, dates, strict=True)):
        evidence = check["证据"]
        if [e["截止日期"] for e in evidence] != expected:
            return False
        current_rows = evidence[:1] if idx == 4 else evidence
        if any(e["报告版本"] != version for e in current_rows):
            return False
    return all(e["起始日期"] == start for e in details[2]["证据"])


def amount(row):
    if not all(
        row[k].strip() for k in ("主体", "范围", "报告版本", "行名", "页", "证据编号")
    ):
        raise ValueError("缺少原行定位")
    if row["币种"] != "CNY" or row["原单位"] not in UNITS:
        raise ValueError("需明确人民币披露单位")
    if not AMOUNT.fullmatch(row["原始金额"]):
        raise ValueError("需明确十进制原始金额")
    return Decimal(row["原始金额"]) * UNITS[row["原单位"]]


def calculate(args):
    current = args["current"]
    previous = args.get("previous")
    evidence = [current]

    def result(status, formula="", value=None):
        return {
            "status": status,
            "formula": formula,
            "yuan": None if value is None else format(value, "f"),
            "evidence": evidence,
        }

    with localcontext() as ctx:
        ctx.prec = 64
        try:
            end = date.fromisoformat(current["截止日期"])
            value = amount(current)
        except ValueError as exc:
            return result(str(exc))
        if (
            end.month not in (3, 6, 9, 12)
            or end.day != monthrange(end.year, end.month)[1]
        ):
            return result("需自然年度季末原行")
        if not verified(current, args["current_checks"]):
            return result("本期四式核验不足")
        if current["表名"] == "资产负债表" and not current["起始日期"]:
            return result("时点值", "本期原值", value)
        if (
            current["表名"] not in ("利润表", "现金流量表")
            or current["起始日期"] != f"{end.year}-01-01"
        ):
            return result("需当年年初至季末的累计流量")
        if end.month == 3:
            return result("已还原", "一季度累计额", value)
        if previous is None:
            return result("缺相邻累计期")
        evidence.append(previous)
        previous_end = date(
            end.year, end.month - 3, monthrange(end.year, end.month - 3)[1]
        )
        if previous["截止日期"] != previous_end.isoformat():
            return result("缺相邻累计期")
        if any(
            previous[k] != current[k]
            for k in ("主体", "范围", "行名", "表名", "起始日期", "币种")
        ):
            return result("相邻累计期口径不符")
        # Version identifiers can differ across reports. The author supplies the
        # exact compatible pair from the disclosure history, including restatements.
        if args.get("comparable_versions") != [
            previous["报告版本"],
            current["报告版本"],
        ]:
            return result("需确认可比版本链")
        if not verified(previous, args.get("previous_checks")):
            return result("前期四式核验不足")
        try:
            prev = amount(previous)
        except ValueError as exc:
            return result(str(exc))
        return result("已还原", "本期累计额减相邻前期累计额", value - prev)


if __name__ == "__main__":
    args = json.loads(
        (Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json").read_text()
    )
    (Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json").write_text(
        json.dumps({"result": calculate(args)}, ensure_ascii=False), encoding="utf-8"
    )
