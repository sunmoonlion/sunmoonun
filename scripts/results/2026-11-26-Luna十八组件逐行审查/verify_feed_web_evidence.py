"""相对链接、订阅条目标识、正文标题和报告版别的离线对照。"""
from app.application.ports.supply import Page
from app.application.supply.web import WebSite
from app.application.supply.readings import recognize_periodic, text_reading
from tests.test_supply_web import channel, FakeHttp


async def test_relative_feed_entry_uses_original_directory_after_redirect():
    source = "https://www.stats.gov.cn/a/feed.xml"
    final = "https://www.stats.gov.cn/b/feed.xml"
    body = b"<rss><channel><item><link>report.html</link></item></channel></rss>"
    site = WebSite(FakeHttp({source: Page(200, "application/rss+xml", body, final)}),
                   channel(obey_robots=False))
    entries, _ = await site.watch(source, {})
    assert entries[0].url == "https://www.stats.gov.cn/a/report.html"


async def test_duplicate_item_in_one_feed_is_returned_twice():
    url = "https://www.stats.gov.cn/feed.xml"
    item = b"<item><link>/report.html</link></item>"
    feed = b"<rss><channel>" + item * 2 + b"</channel></rss>"
    site = WebSite(FakeHttp({url: Page(200,"application/rss+xml",feed,url)}),
                   channel(obey_robots=False))
    entries, _ = await site.watch(url, {})
    assert len(entries) == 2 and entries[0] == entries[1]


def test_multiline_summary_cover_is_taken_as_full_report():
    result = recognize_periodic([{"page": 1, "text": "证券代码：600009\n2025年年度报告\n摘要"}])
    assert result is not None and result.edition == "full"


def test_markdown_media_type_case_changes_title():
    content = "# 年报\n\n正文".encode()
    assert text_reading(content, "text/markdown").title == "年报"
    assert text_reading(content, "Text/Markdown").title is None
