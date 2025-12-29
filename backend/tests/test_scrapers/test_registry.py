import pytest
from app.scrapers.registry import ScraperRegistry, scraper_plugin
from app.scrapers.base import ScraperPlugin


def test_registry_singleton():
    r1 = ScraperRegistry()
    r2 = ScraperRegistry()
    assert r1 is r2


def test_scraper_plugin_decorator():
    @scraper_plugin(name="test", display_name="Test", version="1.0")
    class TestScraper(ScraperPlugin):
        async def scrape(self, config, keywords):
            return []
        def validate_config(self, config):
            return True

    assert TestScraper.name == "test"
    assert TestScraper.display_name == "Test"


def test_registry_get_scraper():
    registry = ScraperRegistry()
    registry.clear()  # Reset pour test

    @scraper_plugin(name="mock", display_name="Mock", version="1.0")
    class MockScraper(ScraperPlugin):
        async def scrape(self, config, keywords):
            return []
        def validate_config(self, config):
            return True

    scraper = registry.get("mock")
    assert scraper is not None
    assert isinstance(scraper, MockScraper)
