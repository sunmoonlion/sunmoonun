"""Synthetic financial document titles with explicit disambiguating evidence."""
from datetime import date

import pytest

from app.domain.recognition import recognize
from app.domain.vocabulary import VocabularyError, check_attributes


def test_analyst_commentary_remains_research():
    found = recognize("样本公司2025年年报点评.pdf", "证券研究报告 公司点评 分析师：张三", "pdf")
    assert found.description.doc_type == "research_company"


def test_reporting_year_is_bound_to_report_not_publication_date():
    found = recognize("2026年4月15日披露：样本公司2025年年度报告.pdf")
    assert found.description.period_end == date(2025, 12, 31)


def test_specific_industry_survives_substring_overlap():
    found = recognize("非银行金融行业周报.pdf", "证券研究报告")
    assert found.description.industry == "非银行金融"


def test_descriptive_cover_can_identify_a_generically_named_pdf():
    found = recognize("附件一.pdf", "样本公司 2025年年度报告", "pdf")
    assert found.description.doc_type == "annual_report"


@pytest.mark.parametrize("attributes", [{"forecast": [{}]}, {"frequency": []}])
def test_invalid_shapes_produce_a_field_error(attributes):
    with pytest.raises(VocabularyError, match="forecast|frequency"):
        check_attributes("research_company", attributes)
