"""离线输入核对采集回执，无浏览器、无出站请求。"""
from types import SimpleNamespace

from app.application.collectors.rss import parse_feed
from app.application.collectors.scrapy import ScrapyCollectorAdapter
from app.application.collectors.playwright import PlaywrightCollectorAdapter
from app.application.services import info_crawl_service


def test_rss_with_namespace_misses_article():
    feed = '<rss xmlns="urn:rss"><channel><item><link>https://example.test/a</link></item></channel></rss>'
    assert len(parse_feed(feed.replace(' xmlns="urn:rss"', ''))) == 1
    assert parse_feed(feed) == []


async def test_external_metadata_replaces_collector_provenance():
    rows = await ScrapyCollectorAdapter().discover(url="urn:sample", config={
        "spider_name": "local", "results": [{"url":"urn:sample","metadata":{"collector_source":"different"}}]})
    assert rows[0].metadata["collector_source"] == "different"


async def test_string_false_still_imports_render_results():
    rows = await PlaywrightCollectorAdapter().discover(url="urn:sample", config={
        "enabled": "false", "links":["urn:article"]})
    assert len(rows) == 1


def test_iso_metadata_date_is_discarded(monkeypatch):
    monkeypatch.setattr(info_crawl_service, "trafilatura", SimpleNamespace(
        extract_metadata=lambda _: SimpleNamespace(title="年报", date="2026-04-30"),
        extract=lambda *args, **kwargs: "正文"))
    assert info_crawl_service._extract_html("x","urn:example")[-1] is None
