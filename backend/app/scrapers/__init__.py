"""
Scrapers module

Auto-imports all scraper plugins for registration
"""

# Import plugins to trigger @scraper_plugin decorator
from app.scrapers.plugins.hackernews import HackerNewsScraper
from app.scrapers.plugins.reddit import RedditScraper
from app.scrapers.plugins.devto import DevToScraper
from app.scrapers.plugins.youtube_rss import YouTubeRSSScraper
from app.scrapers.plugins.youtube_trending import YouTubeTrendingScraper
from app.scrapers.plugins.arxiv import ArxivScraper
from app.scrapers.plugins.official_blogs import OfficialBlogsScraper

# Export registry for easy access
from app.scrapers.registry import ScraperRegistry, scraper_plugin

__all__ = [
    'ScraperRegistry',
    'scraper_plugin',
    'HackerNewsScraper',
    'RedditScraper',
    'DevToScraper',
    'YouTubeRSSScraper',
    'YouTubeTrendingScraper',
    'ArxivScraper',
    'OfficialBlogsScraper',
]
