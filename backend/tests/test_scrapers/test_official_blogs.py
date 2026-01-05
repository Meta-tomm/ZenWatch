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
