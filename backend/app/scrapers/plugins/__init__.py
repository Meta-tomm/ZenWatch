# Import all scraper plugins to register them
from app.scrapers.plugins.hackernews import HackerNewsScraper
from app.scrapers.plugins.reddit import RedditScraper
from app.scrapers.plugins.devto import DevToScraper
from app.scrapers.plugins.youtube_rss import YouTubeRSSScraper
from app.scrapers.plugins.youtube_trending import YouTubeTrendingScraper
from app.scrapers.plugins.arxiv import ArxivScraper
from app.scrapers.plugins.official_blogs import OfficialBlogsScraper
from app.scrapers.plugins.github_trending import GitHubTrendingScraper
from app.scrapers.plugins.medium import MediumScraper
from app.scrapers.plugins.twitter_nitter import TwitterNitterScraper

__all__ = [
    "HackerNewsScraper",
    "RedditScraper",
    "DevToScraper",
    "YouTubeRSSScraper",
    "YouTubeTrendingScraper",
    "ArxivScraper",
    "OfficialBlogsScraper",
    "GitHubTrendingScraper",
    "MediumScraper",
    "TwitterNitterScraper",
]
