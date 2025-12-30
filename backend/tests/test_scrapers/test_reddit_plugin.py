import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.scrapers.plugins.reddit import RedditScraper


@pytest.mark.asyncio
async def test_reddit_scraper_validate_config():
    scraper = RedditScraper()

    valid_config = {
        "client_id": "test_id",
        "client_secret": "test_secret",
        "subreddits": ["programming"]
    }
    assert scraper.validate_config(valid_config) == True

    invalid_config = {"client_id": "test"}
    assert scraper.validate_config(invalid_config) == False


@pytest.mark.asyncio
async def test_reddit_scraper_returns_articles(monkeypatch):
    scraper = RedditScraper()

    # Mock OAuth2
    async def mock_get_token(self, client_id, secret):
        return "mock_token"

    # Mock fetch posts
    async def mock_fetch_posts(self, subreddit, token, limit):
        return [{
            'title': 'Python Tutorial',
            'url': 'https://example.com',
            'id': '123',
            'published_at': datetime.now(),
            'upvotes': 100,
            'comments_count': 20
        }]

    monkeypatch.setattr(RedditScraper, '_get_access_token', mock_get_token)
    monkeypatch.setattr(RedditScraper, '_fetch_subreddit_posts', mock_fetch_posts)

    config = {
        "client_id": "test",
        "client_secret": "secret",
        "subreddits": ["programming"],
        "max_articles": 10
    }

    articles = await scraper.scrape(config, ["python"])
    assert len(articles) > 0
    assert articles[0]['title'] == 'Python Tutorial'
