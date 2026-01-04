from typing import List, Dict, Any
from datetime import datetime
import feedparser
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.schemas.scraped_article import ScrapedYouTubeVideo


@scraper_plugin(
    name="youtube_rss",
    display_name="YouTube RSS",
    version="1.0.0"
)
class YouTubeRSSScraper(ScraperPlugin):
    """
    YouTube RSS scraper for channel uploads

    Features:
    - Monitors RSS feeds from subscribed channels
    - No API quota consumption
    - Fast and reliable
    - Runs every 30 minutes
    """

    CACHE_TTL = 1800  # 30 minutes

    def validate_config(self, config: Dict) -> bool:
        """No special config required - fetches channels from DB"""
        return True

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedYouTubeVideo]:
        """
        Scrape new videos from subscribed YouTube channels

        Args:
            config: Scraper configuration (unused, fetches all active channels)
            keywords: Filter videos by keywords (optional)

        Returns:
            List of ScrapedYouTubeVideo objects
        """
        # Implementation in next task
        return []

    def _parse_rss_entry(self, entry: Any, channel: Any) -> ScrapedYouTubeVideo:
        """
        Parse RSS entry to ScrapedYouTubeVideo

        Args:
            entry: feedparser entry object
            channel: YouTubeChannel model instance

        Returns:
            ScrapedYouTubeVideo object
        """
        video_id = entry.yt_videoid

        return ScrapedYouTubeVideo(
            title=entry.title,
            url=entry.link,
            source_type='youtube_rss',
            external_id=video_id,
            content=entry.get('summary', ''),
            author=channel.channel_name,
            published_at=datetime(*entry.published_parsed[:6]),
            tags=[channel.channel_name],
            video_id=video_id,
            channel_id=channel.channel_id,
            channel_name=channel.channel_name,
            thumbnail_url=entry.media_thumbnail[0]['url'] if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail else None,
        )
