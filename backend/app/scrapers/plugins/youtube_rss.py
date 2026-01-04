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

    async def _get_active_channels(self) -> List[Any]:
        """
        Fetch active YouTube channels from database

        Note: This requires database session from scraping task context

        Returns:
            List of active YouTubeChannel model instances
        """
        # This will be injected by the scraping task
        # For now, return empty list to allow testing
        return getattr(self, '_channels', [])

    def _matches_keywords(self, video: ScrapedYouTubeVideo, keywords: List[str]) -> bool:
        """
        Check if video matches any keyword

        Args:
            video: ScrapedYouTubeVideo to check
            keywords: List of keywords to match against

        Returns:
            True if video matches any keyword or if no keywords provided
        """
        if not keywords:
            return True

        text = f"{video.title} {video.content}".lower()
        return any(kw.lower() in text for kw in keywords)

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedYouTubeVideo]:
        """
        Scrape new videos from subscribed YouTube channels

        Args:
            config: Scraper configuration (unused, fetches all active channels)
            keywords: Filter videos by keywords (optional)

        Returns:
            List of ScrapedYouTubeVideo objects
        """
        channels = await self._get_active_channels()

        videos = []
        for channel in channels:
            try:
                # Fetch RSS feed
                feed = feedparser.parse(channel.rss_feed_url)

                if feed.bozo:
                    self.logger.warning(f"Malformed RSS for {channel.channel_name}")
                    continue

                # Parse entries
                for entry in feed.entries:
                    try:
                        video = self._parse_rss_entry(entry, channel)

                        # Optional keyword filtering
                        if keywords and not self._matches_keywords(video, keywords):
                            continue

                        videos.append(video)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse entry: {e}")
                        continue

            except Exception as e:
                self.logger.error(f"RSS error for {channel.channel_name}: {e}")
                continue

        self.logger.info(f"Scraped {len(videos)} videos from {len(channels)} channels")
        return videos

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
            thumbnail_url=entry.media_thumbnail[0]['url'] if (hasattr(entry, 'media_thumbnail') and entry.media_thumbnail and len(entry.media_thumbnail) > 0) else None,
        )
