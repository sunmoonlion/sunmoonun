"""使用 KnowFeed 现行抽表与跨年复核函数，检查每股值和零值的单位证据。"""
from dataclasses import replace
from decimal import Decimal
from app.application.securities.report_extraction.checks import check_unit
from app.application.securities.report_extraction.cross_year import cross_check
from app.domain.securities.report_statements import (
    ExtractedRow, ExtractedStatement, Resolution, ResolvedLine,
)

row = ExtractedRow(8, "基本每股收益", Decimal("0.50"), None)
first = ExtractedStatement("income_statement", 8, "万元", "statement_page",
                           False, (row,), {})
later = replace(first, rows=(replace(row, current=None, prior=Decimal("8.50")),))
compared, = cross_check(first, later, fiscal_year=2025).items
assert compared.earlier == Decimal("0.50") and compared.later == Decimal("8.50")
assert compared.verdict == "agree"

zero = ExtractedRow(8, "投资收益", Decimal(0), None)
found = Resolution({"invest_income": ResolvedLine("invest_income", zero, 1, zero.label)}, (), ())
for unit in ("元", "万元", "百万元"):
    verdict, _ = check_unit(replace(first, unit=unit, rows=(zero,)), found, {"invest_income": Decimal(0)})
    assert verdict == "confirmed"
