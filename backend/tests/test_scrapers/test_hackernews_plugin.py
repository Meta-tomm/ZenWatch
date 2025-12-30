import pytest
from app.scrapers.plugins.hackernews import HackerNewsScraper


@pytest.mark.asyncio
async def test_hackernews_validate_config():
    scraper = HackerNewsScraper()
    assert scraper.validate_config({"max_articles": 50}) == True


@pytest.mark.asyncio
async def test_hackernews_scrape(monkeypatch):
    scraper = HackerNewsScraper()

    async def mock_fetch_story(self, story_id):
        return {
            'title': 'Show HN: New Python Tool',
            'url': 'https://example.com',
            'by': 'author',
            'time': 1234567890,
            'score': 200,
            'descendants': 50
        }

    async def mock_get_top_stories(self):
        return [1, 2, 3]

    monkeypatch.setattr(HackerNewsScraper, '_fetch_story', mock_fetch_story)
    monkeypatch.setattr(HackerNewsScraper, '_get_top_story_ids', mock_get_top_stories)

    articles = await scraper.scrape({"max_articles": 10}, ["python"])
    assert len(articles) > 0
