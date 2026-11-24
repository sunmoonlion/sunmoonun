"""F4 author tool. Input facts are dated F2 deliveries for one subject and scope."""

from calendar import monthrange
from datetime import date
from decimal import Decimal, localcontext
import json
import os
from pathlib import Path
import re

from seasonal_rates import forecast_windows, quarter_label, yuan

METRICS = {"营业收入": "revenue", "归母净利润": "profit", "归属于母公司股东的净利润": "profit"}


def quarter_of(day):
    if day.month not in (3, 6, 9, 12) or day.day != monthrange(day.year, day.month)[1]:
        raise ValueError("需季度末的原行")
    return day.year * 4 + day.month // 3 - 1


def period_index(label):
    if not re.fullmatch(r"[1-9][0-9]{3}Q[1-4]", label):
        raise ValueError("季度须写作YYYYQn")
    return int(label[:4]) * 4 + int(label[-1]) - 1


def observations(args):
    points = {}
    for fact in args["facts"]:
        delivery = fact["delivery"]
        if delivery["status"] != "已还原":
            continue
        evidence = delivery["evidence"]
        if not evidence:
            raise ValueError("单季回执缺少原行")
        row = evidence[0]
        if (row["主体"], row["范围"]) != (args["subject"], args["scope"]):
            raise ValueError("主体或范围不同")
        if row["表名"] != "利润表" or row["币种"] != "CNY":
            raise ValueError("需要人民币利润表单季金额")
        metric = METRICS.get(row["行名"])
        if not metric:
            raise ValueError("指标名称须确认")
        end = date.fromisoformat(row["截止日期"])
        published = date.fromisoformat(fact["available_on"])
        period = quarter_of(end)
        if published < end or not all(r["证据编号"] and r["报告版本"] and r["页"] for r in evidence):
            raise ValueError("披露时间或原行定位不足")
        value = delivery["yuan"]
        if not isinstance(value, str) or not re.fullmatch(r"-?[0-9]{1,36}(?:\.[0-9]{1,12})?", value):
            raise ValueError("单季回执缺有效金额")
        record = (Decimal(value), [dict(version=r["报告版本"], page=r["页"], row=r["证据编号"]) for r in evidence])
        versions = points.setdefault((metric, period), {})
        if published in versions and versions[published] != record:
            raise ValueError("同日出现有分歧的版本，需确认")
        versions[published] = record
    return points


def snapshot(points, metric, origin, cutoff):
    amounts, sources = {}, []
    for (name, period), versions in sorted(points.items()):
        eligible = [day for day in versions if day <= cutoff]
        if name != metric or period > origin or not eligible:
            continue
        chosen = max(eligible)
        amount, evidence = versions[chosen]
        amounts[period] = amount
        sources.append(dict(period=quarter_label(period), available_on=chosen.isoformat(),
                            yuan=yuan(amount), evidence=evidence))
    return amounts, sources


def calculate(args):
    origin = period_index(args["origin"])
    as_of = date.fromisoformat(args["as_of"])
    points = observations(args)

    def at(metric, point, cutoff):
        values, sources = snapshot(points, metric, point, cutoff)
        return {**forecast_windows(values, point, parent_profit=(metric == "profit")), "sources": sources}

    cutoffs = args["backtest_cutoffs"]
    if len(cutoffs) != 4:
        raise ValueError("需要最近四个历史起点的披露截止日")
    parsed = [date.fromisoformat(v) for v in cutoffs]
    for pos, cutoff in enumerate([*parsed, as_of]):
        point = origin - 4 + pos
        next_quarter = point + 1
        following_month = (next_quarter % 4 + 1) * 3
        following_end = date(next_quarter // 4, following_month, monthrange(next_quarter // 4, following_month)[1])
        month = (point % 4 + 1) * 3
        end = date(point // 4, month, monthrange(point // 4, month)[1])
        if cutoff < end or cutoff > as_of:
            raise ValueError("截止日与季度不符")
        # Once target results are available this can no longer be an ex-ante forecast.
        if any(day <= cutoff for (metric, period), versions in points.items()
               if period == next_quarter for day in versions):
            raise ValueError("预测起点已能看到目标季披露")
        if cutoff >= following_end and not any(period == next_quarter for _, period in points):
            raise ValueError("缺少目标季首次披露日期，无法确认历史截止")
    if parsed != sorted(parsed) or len(set([*parsed, as_of])) != 5:
        raise ValueError("回测截止日必须依序且独立")

    with localcontext() as ctx:
        ctx.prec = 64
        current = {metric: at(metric, origin, as_of) for metric in ("revenue", "profit")}
        backtests = []
        for offset, cutoff in enumerate(parsed):
            point = origin - 4 + offset
            actual_period = point + 1
            results = {}
            for metric in current:
                predicted = at(metric, point, cutoff)
                actuals = points.get((metric, actual_period), {})
                seen = [day for day in actuals if day <= as_of]
                observed = None
                if seen:
                    published = min(seen)
                    actual, evidence = actuals[published]
                    observed = dict(yuan=yuan(actual), available_on=published.isoformat(), evidence=evidence)
                results[metric] = dict(prediction=predicted["targets"][0], actual=observed,
                                       missing_ratios=predicted["missing_ratios"], sources=predicted["sources"])
            backtests.append(dict(origin=quarter_label(point), cutoff=cutoff.isoformat(), metrics=results))
        missing = current["profit"]["missing_ratios"]
        incomplete = any(
            t["point_yuan"] is None or t["interval_yuan"] is None
            for metric in current.values() for t in metric["targets"]
        ) or any(
            m["actual"] is None or m["prediction"]["point_yuan"] is None or m["prediction"]["interval_yuan"] is None
            for entry in backtests for m in entry["metrics"].values()
        )
        return dict(status="窗口不足" if incomplete else "已计算", forecast=current, backtests=backtests,
                    profit_point_status=current["profit"]["point_status"],
                    profit_interval_status=current["profit"]["interval_status"],
                    missing_profit_periods=[item["period"] for item in missing],
                    revenue_point_yuan=current["revenue"]["targets"][0]["point_yuan"])


if __name__ == "__main__":
    args = json.loads((Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json").read_text())
    try:
        result = calculate(args)
    except ValueError as exc:
        result = {"status": "需核对资料", "reason": str(exc)}
    (Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json").write_text(
        json.dumps({"result": result}, ensure_ascii=False), encoding="utf-8"
    )
