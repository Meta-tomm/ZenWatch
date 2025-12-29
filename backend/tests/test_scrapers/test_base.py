import pytest
from app.scrapers.base import ScraperPlugin


def test_scraper_plugin_is_abstract():
    with pytest.raises(TypeError):
        ScraperPlugin()


def test_scraper_plugin_requires_scrape_method():
    class InvalidScraper(ScraperPlugin):
        pass

    with pytest.raises(TypeError):
        InvalidScraper()


class ConcreteScraper(ScraperPlugin):
    name = "test"
    display_name = "Test"
    version = "1.0.0"

    async def scrape(self, config, keywords):
        return []

    def validate_config(self, config):
        return True


@pytest.mark.asyncio
async def test_quick_match():
    scraper = ConcreteScraper()
    keywords = ["python", "django"]

    assert await scraper._quick_match("Learn Python Programming", keywords) == True
    assert await scraper._quick_match("Django REST Framework", keywords) == True
    assert await scraper._quick_match("Java Spring Boot", keywords) == False
