# Arxiv Scraper Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create an Arxiv scraper plugin to fetch AI/ML research papers from arxiv.org.

**Architecture:** Follows existing scraper plugin pattern (base.py + registry decorator). Uses Arxiv API with XML parsing via xml.etree.ElementTree (stdlib, no extra dependencies).

**Tech Stack:** Python, httpx (async HTTP), xml.etree.ElementTree (XML parsing), Pydantic (validation)

---

## Task 1: Write the failing test for ArxivScraper

**Files:**
- Create: `backend/tests/test_scrapers/test_arxiv_plugin.py`

**Step 1: Write the failing test**

```python
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
```

**Step 2: Run test to verify it fails**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_arxiv_plugin.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.scrapers.plugins.arxiv'"

**Step 3: Commit**

```bash
git add backend/tests/test_scrapers/test_arxiv_plugin.py
git commit -m "test: add failing tests for ArxivScraper"
```

---

## Task 2: Create ArxivScraper plugin skeleton

**Files:**
- Create: `backend/app/scrapers/plugins/arxiv.py`

**Step 1: Write minimal implementation to make tests pass**

```python
from typing import List, Dict, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote

from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.scrapers.strategies.rate_limit import RateLimiter
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="arxiv",
    display_name="arXiv",
    version="1.0.0"
)
class ArxivScraper(ScraperPlugin):
    """
    arXiv scraper using the arXiv API

    API docs: https://info.arxiv.org/help/api/index.html
    Rate limit: ~3 req/s (official recommendation)

    Features:
    - Searches in cs.AI, cs.CL, cs.LG, cs.MA categories
    - Filters by keywords in title/abstract
    - Parses Atom XML response
    - Returns validated Pydantic models
    """

    # Configuration
    MAX_RETRIES = 3
    CACHE_TTL = 3600  # 1 hour (research papers don't change often)
    TIMEOUT = 30.0

    # Arxiv categories for AI/ML research
    CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.MA"]

    # XML namespaces
    ATOM_NS = {'atom': 'http://www.w3.org/2005/Atom'}
    ARXIV_NS = {'arxiv': 'http://arxiv.org/schemas/atom'}

    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        self.rate_limiter = RateLimiter(requests_per_minute=30)
        self.base_url = "https://export.arxiv.org/api/query"

    def validate_config(self, config: Dict) -> bool:
        """No special config required for arXiv"""
        return True

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape papers from arXiv

        Strategy:
        1. Build search query with categories and keywords
        2. Fetch XML response from arXiv API
        3. Parse entries and filter by keywords
        4. Return validated ScrapedArticle objects
        """
        max_articles = config.get('max_articles', 50)

        self.logger.info(f"Fetching arXiv papers for keywords: {keywords}")

        articles = []
        errors = 0

        # Build and execute search query
        try:
            xml_response = await self._fetch_papers(keywords, max_articles)
            root = ET.fromstring(xml_response)

            # Parse each entry
            for entry in root.findall('atom:entry', self.ATOM_NS):
                try:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                except Exception as e:
                    errors += 1
                    self.logger.warning(f"Failed to parse arXiv entry: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to fetch arXiv papers: {e}")
            return []

        self.logger.info(
            f"Fetched {len(articles)} arXiv papers "
            f"({errors} errors skipped)"
        )

        return articles[:max_articles]

    async def _fetch_papers(self, keywords: List[str], max_results: int) -> str:
        """
        Fetch papers from arXiv API

        Query format:
        - Categories: (cat:cs.AI OR cat:cs.CL OR ...)
        - Keywords: AND (all:keyword1 OR all:keyword2 OR ...)
        """
        # Build category query
        cat_query = " OR ".join(f"cat:{cat}" for cat in self.CATEGORIES)

        # Build keyword query (search in all fields: title, abstract, authors)
        if keywords:
            kw_query = " OR ".join(f"all:{quote(kw)}" for kw in keywords)
            search_query = f"({cat_query}) AND ({kw_query})"
        else:
            search_query = f"({cat_query})"

        async with self.rate_limiter:
            params = {
                'search_query': search_query,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }

            response = await self._retry_request(
                'GET',
                self.base_url,
                params=params
            )

            return response.text

    def _parse_entry(self, entry: ET.Element) -> Optional[ScrapedArticle]:
        """
        Parse arXiv Atom entry to ScrapedArticle

        Returns None if required fields are missing
        """
        try:
            # Extract title (remove newlines and extra whitespace)
            title_elem = entry.find('atom:title', self.ATOM_NS)
            if title_elem is None or not title_elem.text:
                return None
            title = ' '.join(title_elem.text.split())

            # Extract ID (format: http://arxiv.org/abs/2401.00001v1)
            id_elem = entry.find('atom:id', self.ATOM_NS)
            if id_elem is None or not id_elem.text:
                return None
            arxiv_id = id_elem.text.split('/')[-1]  # Get "2401.00001v1"

            # Extract URL (link with rel="alternate")
            url = None
            for link in entry.findall('atom:link', self.ATOM_NS):
                if link.get('rel') == 'alternate':
                    url = link.get('href')
                    break
            if not url:
                url = id_elem.text

            # Extract abstract/summary
            summary_elem = entry.find('atom:summary', self.ATOM_NS)
            content = ' '.join(summary_elem.text.split()) if summary_elem is not None and summary_elem.text else None

            # Extract authors (join multiple authors)
            authors = []
            for author in entry.findall('atom:author', self.ATOM_NS):
                name_elem = author.find('atom:name', self.ATOM_NS)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text)
            author_str = ', '.join(authors) if authors else None

            # Extract published date
            published_elem = entry.find('atom:published', self.ATOM_NS)
            if published_elem is not None and published_elem.text:
                # Format: 2024-01-15T10:30:00Z
                published_at = datetime.fromisoformat(
                    published_elem.text.replace('Z', '+00:00')
                )
            else:
                published_at = datetime.now()

            # Extract primary category as tag
            tags = []
            primary_cat = entry.find('arxiv:primary_category', self.ARXIV_NS)
            if primary_cat is not None:
                tags.append(primary_cat.get('term', ''))

            # Create validated ScrapedArticle
            return ScrapedArticle(
                title=title,
                url=url,
                source_type='arxiv',
                external_id=arxiv_id,
                content=content,
                author=author_str,
                published_at=published_at,
                tags=tags,
                upvotes=0,  # arXiv doesn't have upvotes
                comments_count=0,
                raw_data={'arxiv_id': arxiv_id, 'authors': authors}
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse arXiv entry: {e}")
            return None
```

**Step 2: Run tests to verify they pass**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_arxiv_plugin.py -v`
Expected: All 3 tests PASS

**Step 3: Commit**

```bash
git add backend/app/scrapers/plugins/arxiv.py
git commit -m "feat(scrapers): add ArxivScraper plugin for research papers"
```

---

## Task 3: Add integration test with real API (optional, marked skip by default)

**Files:**
- Modify: `backend/tests/test_scrapers/test_arxiv_plugin.py`

**Step 1: Add integration test**

Add to the end of the test file:

```python
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
```

**Step 2: Run unit tests to verify they still pass**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_arxiv_plugin.py -v`
Expected: 3 tests PASS, 1 skipped

**Step 3: Commit**

```bash
git add backend/tests/test_scrapers/test_arxiv_plugin.py
git commit -m "test: add integration test for ArxivScraper (skipped by default)"
```

---

## Task 4: Verify scraper registration and linting

**Files:**
- None (verification only)

**Step 1: Verify scraper is registered**

```bash
cd backend && poetry run python -c "
from app.scrapers.registry import ScraperRegistry
from app.scrapers.plugins import arxiv  # Force import

registry = ScraperRegistry()
plugins = registry.list_plugins()
print('Registered plugins:', list(plugins.keys()))
assert 'arxiv' in plugins, 'ArxivScraper not registered!'
print('ArxivScraper registered successfully!')
"
```

Expected: "ArxivScraper registered successfully!"

**Step 2: Run linter**

Run: `cd backend && poetry run ruff check app/scrapers/plugins/arxiv.py`
Expected: No errors

**Step 3: Run type checker (if available)**

Run: `cd backend && poetry run mypy app/scrapers/plugins/arxiv.py --ignore-missing-imports`
Expected: No errors or minor warnings only

**Step 4: Run all scraper tests to ensure no regressions**

Run: `cd backend && poetry run pytest tests/test_scrapers/ -v`
Expected: All tests pass

**Step 5: Commit (if any fixes were needed)**

```bash
git add -A
git commit -m "fix: address linting issues in ArxivScraper"
```

---

## Summary

This plan creates an arXiv scraper that:
1. Uses the official arXiv API (Atom XML format)
2. Searches in AI/ML categories: cs.AI, cs.CL, cs.LG, cs.MA
3. Filters by keywords in title/abstract
4. Follows existing scraper patterns (base class, registry decorator, rate limiting)
5. Returns validated ScrapedArticle objects with title, URL, abstract, authors, date
6. Uses stdlib xml.etree.ElementTree (no new dependencies)

---

**Plan complete and saved to `docs/plans/2026-01-05-arxiv-scraper.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
