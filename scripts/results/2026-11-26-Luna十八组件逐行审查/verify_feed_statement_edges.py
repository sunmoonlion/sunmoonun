"""用原始 PDF 词与坐标核对财报行和补充资料。"""
from decimal import Decimal
from app.application.securities.report_extraction.layout import amount, is_number
from app.application.securities.report_extraction.supplement import extract_supplement
from app.domain.securities.report_statements import PageWords, Word


def test_one_sided_parentheses_yield_opposite_amounts():
    assert is_number("123.00)") and is_number("(123.00")
    assert amount("123.00)") == Decimal("123")
    assert amount("(123.00") == Decimal("-123")


def test_unit_on_second_header_line_is_lost():
    page = PageWords(1, (
        Word("现金流量表补充资料", 0, 70, 0),
        Word("项目", 0, 30, 10),
        Word("单位：万元", 0, 55, 20),
        Word("无形资产摊销", 0, 60, 30),
        Word("12.00", 95, 120, 30), Word("11.00", 155, 180, 30),
    ))
    receipt = extract_supplement([page])
    assert receipt.found["amortization_intangibles"].current == Decimal("12")
    assert receipt.unit is None


def test_page_after_complete_statements_is_consumed_before_supplement():
    from app.application.securities.report_extraction import extract_statements
    from tests.test_report_extraction import page, report, row

    note = page(90, row("现金流量表补充资料"), row("单位：元"),
                row("无形资产摊销", "12.00", "11.00"))
    stream = iter([*report(), note])
    assert len(extract_statements(stream).statements) == 3
    assert extract_supplement(stream).start_page is None
    assert extract_supplement([note]).start_page == 90
