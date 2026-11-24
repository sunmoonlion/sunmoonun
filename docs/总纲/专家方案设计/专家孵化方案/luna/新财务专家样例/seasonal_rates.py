"""Author's F1 and F4 arithmetic for already verified, comparable CNY amounts."""

from statistics import median


def yuan(value):
    whole, dot, fraction = format(value, "f").partition(".")
    return (whole + dot + fraction.rstrip("0")).rstrip(".")


def year_on_year(current, prior, *, parent_profit):
    change = current - prior
    description = f"变动{yuan(change)}元"
    if parent_profit and prior < 0:
        if current > 0:
            description = f"扭亏为盈，变动{yuan(change)}元"
        elif current == 0:
            description = f"弥补亏损{yuan(change)}元"
        elif change > 0:
            description = f"减亏{yuan(change)}元"
        elif change < 0:
            description = f"增亏{yuan(-change)}元"
        else:
            description = "亏损持平"
        reason = "同期归母净利润为负"
    elif prior == 0:
        reason = "同期基数为零"
    else:
        reason = ""
    return {
        "change_yuan": yuan(change),
        "description": description,
        "percent_status": "不适用" if reason else "可算",
        "reason": reason,
        "rate": None if reason else change / prior,
    }


def quarter_label(index):
    year, offset = divmod(index, 4)
    return f"{year}Q{offset + 1}"


def forecast_windows(history, origin, *, parent_profit):
    """history maps year*4+quarter-1 to a Decimal from the as-of snapshot."""
    rates = []
    missing = []
    for period in range(origin - 7, origin + 1):
        current = history.get(period)
        prior = history.get(period - 4)
        if current is None or prior is None:
            reason = "比较期金额缺失"
            rate = None
        else:
            comparison = year_on_year(current, prior, parent_profit=parent_profit)
            rate, reason = comparison["rate"], comparison["reason"]
        rates.append(rate)
        if reason:
            missing.append({"period": quarter_label(period), "reason": reason})

    point_rate = median(rates[-4:]) if None not in rates[-4:] else None
    bounds = (min(rates), max(rates)) if None not in rates else None
    targets = []
    for period in (origin + 1, origin + 2):
        base = history.get(period - 4)
        point = None if base is None or point_rate is None else base * (1 + point_rate)
        interval = None
        if base is not None and bounds is not None:
            interval = sorted(base * (1 + rate) for rate in bounds)
        targets.append({
            "period": quarter_label(period),
            "base_period": quarter_label(period - 4),
            "point_yuan": None if point is None else yuan(point),
            "interval_yuan": None if interval is None else [yuan(v) for v in interval],
            "base_missing": base is None,
        })
    return {
        "point_status": "窗口缺项" if point_rate is None else "可算",
        "interval_status": "窗口缺项" if bounds is None else "可算",
        "missing_ratios": missing,
        "targets": targets,
    }
