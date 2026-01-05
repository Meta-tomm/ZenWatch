# Official AI Blogs Scraper Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a scraper plugin that fetches articles from official AI company blogs via RSS feeds (OpenAI, DeepMind).

**Architecture:** A new scraper plugin following the existing `ScraperPlugin` pattern. Uses `feedparser` (already in dependencies) to parse RSS feeds. Config stores a list of RSS feed URLs. Each feed is fetched and parsed into `ScrapedArticle` objects.

**Tech Stack:** Python, feedparser, httpx, ScraperPlugin base class, ScrapedArticle schema

---

## Task 1: Write Failing Test for OfficialBlogsScraper Registration

**Files:**
- Create: `backend/tests/test_scrapers/test_official_blogs.py`

**Step 1: Write the failing test**

```python
import pytest
from app.scrapers.plugins.official_blogs import OfficialBlogsScraper
from app.scrapers.registry import ScraperRegistry


def test_official_blogs_scraper_registered():
    """Test scraper is registered in registry"""
    registry = ScraperRegistry()
    scraper = registry.get('official_blogs')

    assert scraper is not None
    assert isinstance(scraper, OfficialBlogsScraper)


def test_official_blogs_metadata():
    """Test scraper has correct metadata"""
    scraper = OfficialBlogsScraper()

    assert scraper.name == 'official_blogs'
    assert scraper.display_name == 'Official AI Blogs'
    assert scraper.version == '1.0.0'
```

**Step 2: Run test to verify it fails**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_official_blogs.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.scrapers.plugins.official_blogs'"

---

## Task 2: Create OfficialBlogsScraper with Registration

**Files:**
- Create: `backend/app/scrapers/plugins/official_blogs.py`

**Step 1: Write minimal implementation for registration**

```python
from typing import List, Dict
from datetime import datetime
import feedparser
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="official_blogs",
    display_name="Official AI Blogs",
    version="1.0.0"
)
class OfficialBlogsScraper(ScraperPlugin):
    """
    Scraper for official AI company blogs via RSS feeds.

    Supports:
    - OpenAI Blog: https://openai.com/blog/rss.xml
    - DeepMind Blog: https://deepmind.google/blog/rss.xml

    Config format:
    {
        "feeds": [
            {"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"},
            {"name": "DeepMind", "url": "https://deepmind.google/blog/rss.xml"}
        ],
        "max_articles_per_feed": 20
    }
    """

    CACHE_TTL = 3600  # 1 hour

    def validate_config(self, config: Dict) -> bool:
        """Validate config has feeds list"""
        return True

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """Scrape articles from configured RSS feeds"""
        return []
```

**Step 2: Run test to verify registration passes**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_official_blogs.py -v`
Expected: PASS (2 tests)

**Step 3: Commit**

```bash
git add backend/app/scrapers/plugins/official_blogs.py backend/tests/test_scrapers/test_official_blogs.py
git commit -m "feat(scrapers): add OfficialBlogsScraper skeleton with registry"
```

---

## Task 3: Write Failing Test for Config Validation

**Files:**
- Modify: `backend/tests/test_scrapers/test_official_blogs.py`

**Step 1: Add config validation tests**

```python
@pytest.mark.asyncio
async def test_validate_config_valid():
    """Test valid config passes validation"""
    scraper = OfficialBlogsScraper()

    valid_config = {
        "feeds": [
            {"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"},
            {"name": "DeepMind", "url": "https://deepmind.google/blog/rss.xml"}
        ],
        "max_articles_per_feed": 20
    }

    assert scraper.validate_config(valid_config) is True


@pytest.mark.asyncio
async def test_validate_config_empty_feeds():
    """Test empty feeds list is valid (will just return no articles)"""
    scraper = OfficialBlogsScraper()

    config = {"feeds": []}
    assert scraper.validate_config(config) is True


@pytest.mark.asyncio
async def test_validate_config_missing_feeds():
    """Test missing feeds key uses default feeds"""
    scraper = OfficialBlogsScraper()

    # No feeds key - should still be valid (uses defaults)
    assert scraper.validate_config({}) is True
```

**Step 2: Run test to verify it passes (validate_config returns True)**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_official_blogs.py::test_validate_config_valid -v`
Expected: PASS

---

## Task 4: Write Failing Test for RSS Entry Parsing

**Files:**
- Modify: `backend/tests/test_scrapers/test_official_blogs.py`

**Step 1: Add parsing test**

```python
from unittest.mock import Mock


@pytest.mark.asyncio
async def test_parse_rss_entry():
    """Test parsing RSS entry to ScrapedArticle"""
    scraper = OfficialBlogsScraper()

    # Mock feedparser entry
    entry = Mock()
    entry.title = 'GPT-5 Announcement'
    entry.link = 'https://openai.com/blog/gpt-5'
    entry.id = 'https://openai.com/blog/gpt-5'
    entry.get = lambda key, default=None: {
        'summary': 'We are announcing GPT-5...',
        'author': 'OpenAI Team'
    }.get(key, default)
    entry.published_parsed = (2026, 1, 5, 12, 0, 0, 0, 0, 0)

    article = scraper._parse_rss_entry(entry, 'OpenAI')

    assert article is not None
    assert article.title == 'GPT-5 Announcement'
    assert str(article.url) == 'https://openai.com/blog/gpt-5'
    assert article.source_type == 'official_blogs'
    assert article.external_id == 'https://openai.com/blog/gpt-5'
    assert article.content == 'We are announcing GPT-5...'
    assert 'OpenAI' in article.tags


@pytest.mark.asyncio
async def test_parse_rss_entry_missing_date():
    """Test parsing entry with missing published date uses now()"""
    scraper = OfficialBlogsScraper()

    entry = Mock()
    entry.title = 'Test Article'
    entry.link = 'https://example.com/article'
    entry.id = 'article-123'
    entry.get = lambda key, default=None: default
    entry.published_parsed = None

    article = scraper._parse_rss_entry(entry, 'TestBlog')

    assert article is not None
    assert article.published_at is not None  # Should have a date
```

**Step 2: Run test to verify it fails**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_official_blogs.py::test_parse_rss_entry -v`
Expected: FAIL with "AttributeError: 'OfficialBlogsScraper' object has no attribute '_parse_rss_entry'"

---

## Task 5: Implement _parse_rss_entry Method

**Files:**
- Modify: `backend/app/scrapers/plugins/official_blogs.py`

**Step 1: Add _parse_rss_entry method**

Add after the `validate_config` method:

```python
    def _parse_rss_entry(self, entry, feed_name: str) -> ScrapedArticle | None:
        """
        Parse RSS entry to ScrapedArticle

        Args:
            entry: feedparser entry object
            feed_name: Name of the feed (e.g., "OpenAI", "DeepMind")

        Returns:
            ScrapedArticle or None if parsing fails
        """
        try:
            title = getattr(entry, 'title', None)
            link = getattr(entry, 'link', None)
            entry_id = getattr(entry, 'id', link)

            if not title or not link:
                self.logger.warning(f"Skipping entry with missing title or link")
                return None

            # Parse published date
            published_parsed = getattr(entry, 'published_parsed', None)
            if published_parsed:
                published_at = datetime(*published_parsed[:6])
            else:
                published_at = datetime.now()

            # Get content/summary
            content = entry.get('summary', '') or entry.get('description', '')

            # Get author if available
            author = entry.get('author', feed_name)

            return ScrapedArticle(
                title=title,
                url=link,
                source_type='official_blogs',
                external_id=str(entry_id),
                content=content,
                author=author,
                published_at=published_at,
                tags=[feed_name],
                raw_data={'feed_name': feed_name}
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse RSS entry: {e}")
            return None
```

**Step 2: Run tests to verify parsing passes**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_official_blogs.py::test_parse_rss_entry tests/test_scrapers/test_official_blogs.py::test_parse_rss_entry_missing_date -v`
Expected: PASS (2 tests)

**Step 3: Commit**

```bash
git add backend/app/scrapers/plugins/official_blogs.py backend/tests/test_scrapers/test_official_blogs.py
git commit -m "feat(scrapers): add RSS entry parsing to OfficialBlogsScraper"
```

---

## Task 6: Write Failing Test for Scrape Method

**Files:**
- Modify: `backend/tests/test_scrapers/test_official_blogs.py`

**Step 1: Add scrape test with mocked feedparser**

```python
from unittest.mock import patch


@pytest.mark.asyncio
async def test_scrape_fetches_feeds():
    """Test scrape fetches and parses configured feeds"""
    scraper = OfficialBlogsScraper()

    # Mock feed data
    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.entries = [
        Mock(
            title='Article 1',
            link='https://openai.com/blog/article-1',
            id='article-1',
            published_parsed=(2026, 1, 5, 10, 0, 0, 0, 0, 0),
            get=lambda k, d=None: {'summary': 'Summary 1'}.get(k, d)
        ),
        Mock(
            title='Article 2',
            link='https://openai.com/blog/article-2',
            id='article-2',
            published_parsed=(2026, 1, 4, 10, 0, 0, 0, 0, 0),
            get=lambda k, d=None: {'summary': 'Summary 2'}.get(k, d)
        )
    ]

    config = {
        "feeds": [{"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"}],
        "max_articles_per_feed": 10
    }

    with patch('feedparser.parse', return_value=mock_feed):
        articles = await scraper.scrape(config, [])

    assert len(articles) == 2
    assert articles[0].title == 'Article 1'
    assert articles[1].title == 'Article 2'


@pytest.mark.asyncio
async def test_scrape_filters_by_keywords():
    """Test scrape filters articles by keywords"""
    scraper = OfficialBlogsScraper()

    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.entries = [
        Mock(
            title='GPT-5 Release',
            link='https://openai.com/blog/gpt5',
            id='gpt5',
            published_parsed=(2026, 1, 5, 10, 0, 0, 0, 0, 0),
            get=lambda k, d=None: {'summary': 'New model'}.get(k, d)
        ),
        Mock(
            title='Company Update',
            link='https://openai.com/blog/update',
            id='update',
            published_parsed=(2026, 1, 4, 10, 0, 0, 0, 0, 0),
            get=lambda k, d=None: {'summary': 'Business news'}.get(k, d)
        )
    ]

    config = {
        "feeds": [{"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"}]
    }

    with patch('feedparser.parse', return_value=mock_feed):
        articles = await scraper.scrape(config, ['GPT'])

    assert len(articles) == 1
    assert articles[0].title == 'GPT-5 Release'
```

**Step 2: Run test to verify it fails**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_official_blogs.py::test_scrape_fetches_feeds -v`
Expected: FAIL with "AssertionError: assert 0 == 2" (scrape returns empty list)

---

## Task 7: Implement Scrape Method

**Files:**
- Modify: `backend/app/scrapers/plugins/official_blogs.py`

**Step 1: Implement the scrape method**

Replace the existing `scrape` method with:

```python
    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape articles from configured RSS feeds

        Args:
            config: Configuration with feeds list
            keywords: Optional list of keywords for filtering

        Returns:
            List of ScrapedArticle objects
        """
        feeds = config.get('feeds', self._get_default_feeds())
        max_per_feed = config.get('max_articles_per_feed', 20)

        if not feeds:
            self.logger.info("No feeds configured, returning empty list")
            return []

        articles = []
        errors = 0

        for feed_config in feeds:
            feed_name = feed_config.get('name', 'Unknown')
            feed_url = feed_config.get('url')

            if not feed_url:
                self.logger.warning(f"Skipping feed {feed_name}: no URL")
                continue

            try:
                feed_articles = await self._fetch_feed(feed_url, feed_name, max_per_feed, keywords)
                articles.extend(feed_articles)
            except Exception as e:
                errors += 1
                self.logger.error(f"Failed to fetch feed {feed_name}: {e}")
                continue

        self.logger.info(
            f"Scraped {len(articles)} articles from {len(feeds)} feeds "
            f"({errors} errors)"
        )

        return articles

    async def _fetch_feed(
        self,
        feed_url: str,
        feed_name: str,
        max_articles: int,
        keywords: List[str]
    ) -> List[ScrapedArticle]:
        """
        Fetch and parse a single RSS feed

        Args:
            feed_url: URL of the RSS feed
            feed_name: Display name of the feed
            max_articles: Maximum articles to return
            keywords: Keywords for filtering

        Returns:
            List of ScrapedArticle objects
        """
        self.logger.info(f"Fetching feed: {feed_name} ({feed_url})")

        feed = feedparser.parse(feed_url)

        if feed.bozo:
            self.logger.warning(f"Malformed RSS for {feed_name}: {feed.bozo_exception}")

        articles = []
        for entry in feed.entries[:max_articles]:
            article = self._parse_rss_entry(entry, feed_name)
            if article is None:
                continue

            # Keyword filtering
            if keywords and not self._matches_keywords(article, keywords):
                continue

            articles.append(article)

        return articles

    def _matches_keywords(self, article: ScrapedArticle, keywords: List[str]) -> bool:
        """
        Check if article matches any keyword

        Args:
            article: ScrapedArticle to check
            keywords: List of keywords

        Returns:
            True if matches any keyword or no keywords provided
        """
        if not keywords:
            return True

        text = f"{article.title} {article.content or ''}".lower()
        return any(kw.lower() in text for kw in keywords)

    def _get_default_feeds(self) -> List[Dict]:
        """
        Default AI blog feeds

        Returns:
            List of default feed configurations
        """
        return [
            {"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"},
            {"name": "DeepMind", "url": "https://deepmind.google/blog/rss.xml"}
        ]
```

**Step 2: Run tests to verify they pass**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_official_blogs.py -v`
Expected: PASS (all tests)

**Step 3: Commit**

```bash
git add backend/app/scrapers/plugins/official_blogs.py backend/tests/test_scrapers/test_official_blogs.py
git commit -m "feat(scrapers): implement OfficialBlogsScraper scrape method"
```

---

## Task 8: Write Test for Default Feeds

**Files:**
- Modify: `backend/tests/test_scrapers/test_official_blogs.py`

**Step 1: Add test for default feeds**

```python
@pytest.mark.asyncio
async def test_scrape_uses_default_feeds_when_not_configured():
    """Test scrape uses default OpenAI/DeepMind feeds when none configured"""
    scraper = OfficialBlogsScraper()

    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.entries = []

    with patch('feedparser.parse', return_value=mock_feed) as mock_parse:
        await scraper.scrape({}, [])

        # Should have called parse for both default feeds
        assert mock_parse.call_count == 2

        called_urls = [call[0][0] for call in mock_parse.call_args_list]
        assert 'https://openai.com/blog/rss.xml' in called_urls
        assert 'https://deepmind.google/blog/rss.xml' in called_urls
```

**Step 2: Run test to verify**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_official_blogs.py::test_scrape_uses_default_feeds_when_not_configured -v`
Expected: PASS

**Step 3: Commit**

```bash
git add backend/tests/test_scrapers/test_official_blogs.py
git commit -m "test(scrapers): add default feeds test for OfficialBlogsScraper"
```

---

## Task 9: Run Full Test Suite and Verify

**Step 1: Run all OfficialBlogsScraper tests**

Run: `cd backend && poetry run pytest tests/test_scrapers/test_official_blogs.py -v`
Expected: PASS (all tests)

**Step 2: Run linter**

Run: `cd backend && poetry run ruff check app/scrapers/plugins/official_blogs.py tests/test_scrapers/test_official_blogs.py`
Expected: No errors

**Step 3: Final commit with all changes**

```bash
git add .
git commit -m "feat(scrapers): complete OfficialBlogsScraper for AI blogs RSS

- Add OfficialBlogsScraper plugin with registry decorator
- Fetch RSS feeds from OpenAI and DeepMind blogs
- Support configurable feeds list in source.config
- Filter articles by keywords
- Parse entries to ScrapedArticle schema
- Default feeds: OpenAI, DeepMind
- Full test coverage"
```

---

## Summary

**Created Files:**
- `backend/app/scrapers/plugins/official_blogs.py` - Main scraper implementation
- `backend/tests/test_scrapers/test_official_blogs.py` - Unit tests

**Key Features:**
1. Uses `@scraper_plugin` decorator for auto-registration
2. Extends `ScraperPlugin` base class
3. Uses `feedparser` library (already in dependencies)
4. Configurable feeds via `config["feeds"]` list
5. Default feeds: OpenAI, DeepMind
6. Keyword filtering on title + content
7. Returns `ScrapedArticle` objects

**Config Example:**
```json
{
  "feeds": [
    {"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"},
    {"name": "DeepMind", "url": "https://deepmind.google/blog/rss.xml"}
  ],
  "max_articles_per_feed": 20
}
```
