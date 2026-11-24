"""F1 author tool for annual, comparable CNY consolidated accounts."""

from decimal import Decimal, localcontext
import json
import os
from pathlib import Path

from quarter import amount, verified
from seasonal_rates import year_on_year, yuan

ACCOUNTS = {
    "revenue": ("利润表", ("营业收入", "营业总收入")),
    "cost": ("利润表", ("营业成本",)),
    "profit": ("利润表", ("归母净利润", "归属于母公司股东的净利润", "归属于上市公司股东的净利润")),
    "cash": ("现金流量表", ("经营活动产生的现金流量净额",)),
    "equity_open": ("资产负债表", ("归母净资产", "归属于母公司所有者权益合计")),
    "equity_close": ("资产负债表", ("归母净资产", "归属于母公司所有者权益合计")),
}
RATIOS = {
    "gross_margin": ("revenue", "cost", "(营业收入−营业成本)/营业收入"),
    "net_margin": ("profit", "revenue", "归母净利润/营业收入"),
    "cash_to_profit": ("cash", "profit", "经营现金流/归母净利润"),
    "roe": ("profit", "equity_open", "equity_close", "归母净利润/平均归母净资产"),
}


def calculate(args):
    operation = args["metric"]
    measure = args["account"]
    year = args["end_year"]
    evidence = []

    def deliver(status, **fields):
        return {"status": status, "evidence": evidence, **fields}

    def take(annual, account):
        report = args["annual"].get(str(annual))
        if not report:
            raise ValueError(f"缺{annual}年报")
        row = report["rows"].get(account)
        if not row:
            raise ValueError(f"缺{annual}年{account}原行")
        evidence.append(row)
        table, names = ACCOUNTS[account]
        opening = account == "equity_open"
        end = f"{annual - int(opening)}-12-31"
        start = "" if account.startswith("equity_") else f"{annual}-01-01"
        if (row["主体"], row["范围"], row["表名"], row["截止日期"], row["起始日期"]) != (
                args["subject"], args["scope"], table, end, start) or row["行名"] not in names:
            raise ValueError("原行科目、口径或期间不符")
        # Opening equity belongs to this year's filing but is measured on the prior year end.
        if not verified({**row, "截止日期": f"{annual}-12-31"}, report["checks"]):
            raise ValueError("年度四式核验不足")
        return amount(row)

    try:
        with localcontext() as ctx:
            ctx.prec = 64
            if operation in RATIOS:
                *keys, formula = RATIOS[operation]
                values = [take(year, k) for k in keys]
                if operation == "gross_margin":
                    revenue, cost = values
                    numerator, denominator = revenue - cost, revenue
                elif operation == "roe":
                    numerator, opening, closing = values
                    denominator = (opening + closing) / 2
                else:
                    numerator, denominator = values
                if denominator == 0:
                    return deliver("分母不成立", percent_status="不适用", percent=None, formula=formula)
                return deliver("已计算", percent_status="可算", percent=yuan(numerator / denominator * 100), formula=formula)
            if measure not in ("profit", "revenue", "cost"):
                return deliver("需确认指标")
            current = take(year, measure)
            if operation == "amount":
                return deliver("已计算", amount_yuan=yuan(current), formula="报表原行金额折合人民币元")
            start = year - 1 if operation == "yoy" else args.get("start_year")
            if start is None or start >= year:
                return deliver("需明确起止年度")
            prior = take(start, measure)
            if args.get("comparable_versions") != [evidence[1]["报告版本"], evidence[0]["报告版本"]]:
                return deliver("需确认可比版本链")
            if operation == "yoy":
                result = year_on_year(current, prior, parent_profit=measure == "profit")
                rate = result.pop("rate")
                return deliver("已列示", percent=None if rate is None else yuan(rate * 100),
                               current_yuan=yuan(current), prior_yuan=yuan(prior), **result)
            if operation == "cagr":
                if prior <= 0 or current < 0:
                    return deliver("分母或增长根不成立", percent_status="不适用", percent=None)
                return deliver("已计算", percent=yuan(((current/prior) ** (Decimal(1)/(year-start))-1)*100),
                               percent_status="可算", formula="(终值/初值)^(1/年数)−1", years=year-start)
            return deliver("需确认指标")
    except ValueError as exc:
        return deliver(str(exc))


if __name__ == "__main__":
    args = json.loads((Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json").read_text())
    (Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json").write_text(
        json.dumps({"result": calculate(args)}, ensure_ascii=False), encoding="utf-8"
    )
