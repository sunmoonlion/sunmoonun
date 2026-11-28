"""分别用 KnowBase 与 KnowFeed 后端虚拟环境运行，参数为 base 或 feed。"""
import sys
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

app = {"base": "knowbase", "feed": "knowfeed"}[sys.argv[1]]
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / f"{app}-app/{app}-backend/app"))
end = date(2024, 12, 31)
if app == "knowbase":
    from app.domain.chart_of_accounts import METRICS
    from app.domain.user_facts import FactRow, compute_metric
    from app.domain.fact_needs import FactNeed, DatedFact, pick

    profit = FactRow("600000.SH", "IS.NET_PROFIT_PARENT", "归母净利润", Decimal(20),
                     "元", "CNY", end, "year", "consolidated", "original", "年报",
                     1, 1, 5, "standard")
    equity = replace(profit, code="BS.EQUITY_PARENT", duration="instant", value=Decimal(100))
    roe = compute_metric(METRICS["roe_simple"], [profit, equity])
    assert len(roe) == 2 and all(row.value is None for row in roe)
    print("年归母净利 20、期末归母权益 100，ROE 返回两条空值。")

    revenue = replace(profit, code="IS.REVENUE", value=Decimal(100))
    restated = replace(revenue, material_id="restated", value=Decimal(200))
    net = replace(profit, code="IS.NET_PROFIT")
    results = [compute_metric(METRICS["net_margin"], [net, *order])[0]
               for order in [(revenue, restated), (restated, revenue)]]
    assert [row.value for row in results] == [Decimal(".1"), Decimal(".2")]
    print("相同两份披露互换输入次序，净利率依次为 10% 和 20%。")

    march = date(2024, 3, 31)
    request = FactNeed("equity", "季末权益", "600000.SH", march, march, ("BS.EQUITY_PARENT",))
    row = DatedFact(replace(equity, period_end=march), None)
    from app.domain.fact_needs import period_ends
    assert not period_ends(replace(request, duration="instant"))
    assert pick(replace(request, duration="quarter"), [row]).missing
    print("三月末权益用 instant 展不开，改用 quarter 匹配不到已存在的时点行。")
else:
    from app.application.supply.processing import StatementFacts, _one
    from app.domain.securities.report_statements import ExtractedRow, ExtractedStatement, UNIT_ON_STATEMENT

    line = ExtractedRow(5, "基本每股收益（元/股）", Decimal("1.25"), None)
    sheet = ExtractedStatement("income_statement", 5, "万元", UNIT_ON_STATEMENT, False, (line,), {})
    out = StatementFacts()
    _one(out, "income_statement", sheet, end, date(2023, 12, 31), "year")
    assert out.raw[0]["unit"] == "万元" and out.standard == []
    print("原文每股收益 1.25 元/股，原样层却标为万元；该行未进入标准层。")
    from app.application.securities.report_extraction.cross_year import cross_check
    later = replace(sheet, rows=(replace(line, current=None, prior=Decimal("9.25")),))
    [comparison] = cross_check(sheet, later, fiscal_year=2024).items
    assert comparison.earlier != comparison.later and comparison.verdict == "agree"
    print("同年每股收益在两份报告分别列为 1.25 和 9.25，却判为一致。")
