from unittest.mock import Mock, patch

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

    with patch('app.scrapers.plugins.official_blogs.feedparser.parse', return_value=mock_feed):
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

    with patch('app.scrapers.plugins.official_blogs.feedparser.parse', return_value=mock_feed):
        articles = await scraper.scrape(config, ['GPT'])

    assert len(articles) == 1
    assert articles[0].title == 'GPT-5 Release'


@pytest.mark.asyncio
async def test_scrape_uses_default_feeds_when_not_configured():
    """Test scrape uses default OpenAI/DeepMind feeds when none configured"""
    scraper = OfficialBlogsScraper()

    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.entries = []

    with patch('app.scrapers.plugins.official_blogs.feedparser.parse', return_value=mock_feed) as mock_parse:
        await scraper.scrape({}, [])

        # Should have called parse for both default feeds
        assert mock_parse.call_count == 2

        called_urls = [call[0][0] for call in mock_parse.call_args_list]
        assert 'https://openai.com/blog/rss.xml' in called_urls
        assert 'https://deepmind.google/blog/rss.xml' in called_urls