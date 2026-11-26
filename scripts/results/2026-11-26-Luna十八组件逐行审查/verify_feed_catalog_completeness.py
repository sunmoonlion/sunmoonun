"""同一套离线渠道输入核对主题筛选、报告版本、订阅去重与问答身份。"""
from dataclasses import replace
from datetime import date
from app.application.supply.cninfo import CninfoCatalog, _PERIODIC
from app.application.supply.cninfo_irm import CninfoIrmCatalog
from app.application.supply.watch import found_id
from tests.test_supply_cninfo import CategoryHttp, annual, row, window
from tests.test_supply_cninfo_irm import ROWS


async def test_topic_filter_removes_item_with_matching_topic():
    catalog = CninfoCatalog(CategoryHttp())
    full = await catalog.list(window("interim_announcement"))
    filtered = await catalog.list(window("interim_announcement", topics=("results",)))
    assert any("业绩说明会" in e.title and "results" in e.topics for e in full)
    assert not any("业绩说明会" in e.title for e in filtered)


def test_year_title_variants_and_english_filtered_before_edition():
    catalog = CninfoCatalog(CategoryHttp())
    pattern = _PERIODIC["annual_report"][1]
    key = annual(2025)
    assert catalog._report(key, row(1,"示例2025年年度报告"), pattern, 2025)
    assert catalog._report(key, row(1,"示例2025年度报告"), pattern, 2025) is None
    assert catalog._report(replace(key, edition="english"),
        row(2,"2025 Annual Report (English)"), pattern, 2025) is None


def test_long_identity_merges_distinct_revisions():
    entry = CninfoIrmCatalog(None)._entry("000001", ROWS[0])
    first = replace(entry, channel_doc_id="a" * 200, announcement_id="101")
    assert found_id(first) == found_id(replace(first, announcement_id="102"))


def test_foreign_company_row_is_labelled_with_requested_code():
    entry = CninfoIrmCatalog(None)._entry("000002", ROWS[0])
    assert entry.channel_doc_id.startswith("000002:") and "平安银行" in entry.title
