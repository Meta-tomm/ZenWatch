import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch


SAMPLE_ARXIV_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <title>LangChain: A Framework for LLM Applications</title>
    <summary>This paper presents LangChain, a framework for building applications with large language models.</summary>
    <author><name>John Doe</name></author>
    <author><name>Jane Smith</name></author>
    <published>2024-01-15T10:30:00Z</published>
    <link href="http://arxiv.org/abs/2401.00001v1" rel="alternate" type="text/html"/>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="cs.AI"/>
  </entry>
</feed>"""


@pytest.mark.asyncio
async def test_arxiv_validate_config():
    from app.scrapers.plugins.arxiv import ArxivScraper

    scraper = ArxivScraper()
    assert scraper.validate_config({"max_articles": 50}) is True


@pytest.mark.asyncio
async def test_arxiv_parse_entry():
    from app.scrapers.plugins.arxiv import ArxivScraper
    import xml.etree.ElementTree as ET

    scraper = ArxivScraper()
    root = ET.fromstring(SAMPLE_ARXIV_RESPONSE)

    # Find entry element with namespace
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    entry = root.find('atom:entry', ns)

    article = scraper._parse_entry(entry)

    assert article is not None
    assert article.title == "LangChain: A Framework for LLM Applications"
    assert "2401.00001" in article.external_id
    assert article.source_type == "arxiv"
    assert "John Doe" in article.author
    assert "LangChain" in article.content


@pytest.mark.asyncio
async def test_arxiv_scrape_with_mock(monkeypatch):
    from app.scrapers.plugins.arxiv import ArxivScraper
    from unittest.mock import MagicMock

    scraper = ArxivScraper()

    # Mock the HTTP response
    mock_response = MagicMock()
    mock_response.text = SAMPLE_ARXIV_RESPONSE
    mock_response.raise_for_status = MagicMock()

    async def mock_retry_request(self, method, url, **kwargs):
        return mock_response

    monkeypatch.setattr(ArxivScraper, '_retry_request', mock_retry_request)

    async with scraper:
        articles = await scraper.scrape({"max_articles": 10}, ["langchain"])

    assert len(articles) == 1
    assert articles[0].title == "LangChain: A Framework for LLM Applications"


@pytest.mark.asyncio
@pytest.mark.skip(reason="Integration test - requires network access")
async def test_arxiv_real_api():
    """
    Integration test with real arXiv API

    Run with: pytest tests/test_scrapers/test_arxiv_plugin.py -v -k "real_api" --run-integration
    """
    from app.scrapers.plugins.arxiv import ArxivScraper

    scraper = ArxivScraper()

    async with scraper:
        articles = await scraper.scrape(
            {"max_articles": 5},
            ["transformer", "attention"]
        )

    assert len(articles) > 0

    # Verify article structure
    article = articles[0]
    assert article.title
    assert article.url
    assert article.source_type == "arxiv"
    assert article.external_id
    assert article.published_at