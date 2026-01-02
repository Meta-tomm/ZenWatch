"""
Scrapers module

Auto-imports all scraper plugins for registration
"""

# Import plugins to trigger @scraper_plugin decorator
from app.scrapers.plugins.hackernews import HackerNewsScraper
from app.scrapers.plugins.reddit import RedditScraper

# Export registry for easy access
from app.scrapers.registry import ScraperRegistry, scraper_plugin

__all__ = [
    'ScraperRegistry',
    'scraper_plugin',
    'HackerNewsScraper',
    'RedditScraper',
]
