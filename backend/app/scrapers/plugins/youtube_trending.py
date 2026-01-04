from datetime import datetime

import isodate
from googleapiclient.discovery import build

from app.config import settings
from app.schemas.scraped_article import ScrapedYouTubeVideo
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.youtube.quota_manager import YouTubeQuotaManager


@scraper_plugin(
    name="youtube_trending",
    display_name="YouTube Trending",
    version="1.0.0"
)
class YouTubeTrendingScraper(ScraperPlugin):
    """
    YouTube trending videos scraper using Data API v3

    Features:
    - Fetches trending tech videos
    - Filters by keywords
    - Quota-aware (100 units per call)
    """

    CACHE_TTL = 21600  # 6 hours
    MAX_RETRIES = 2

    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        if settings.YOUTUBE_API_KEY:
            self.youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        else:
            self.youtube = None
        self.quota_manager = YouTubeQuotaManager(redis_client) if redis_client else None

    def validate_config(self, config: dict) -> bool:
        """Validate API key is configured"""
        return settings.YOUTUBE_API_KEY is not None

    def _parse_duration(self, iso_duration: str | None) -> int | None:
        """
        Parse ISO 8601 duration to seconds.

        Args:
            iso_duration: ISO 8601 duration string (e.g., "PT4M13S")

        Returns:
            Duration in seconds, or None if parsing fails
        """
        if not iso_duration:
            return None

        try:
            duration = isodate.parse_duration(iso_duration)
            return int(duration.total_seconds())
        except Exception as e:
            self.logger.warning(f"Failed to parse duration '{iso_duration}': {e}")
            return None

    def _parse_trending_video(self, video_data: dict) -> ScrapedYouTubeVideo | None:
        """
        Parse YouTube API video response into ScrapedYouTubeVideo object.

        Args:
            video_data: YouTube API video resource
                Expected structure:
                {
                    "id": "video_id",
                    "snippet": {...},
                    "contentDetails": {"duration": "PT3M33S"},
                    "statistics": {...}
                }

        Returns:
            ScrapedYouTubeVideo object with all fields populated, or None if parsing fails
        """
        # Input validation
        if not video_data or not isinstance(video_data, dict):
            return None

        try:
            video_id = video_data["id"]
            snippet = video_data.get("snippet", {})
            content_details = video_data.get("contentDetails", {})
            statistics = video_data.get("statistics", {})

            # Extract snippet fields
            title = snippet.get("title", "")
            description = snippet.get("description", "")
            channel_id = snippet.get("channelId", "")
            channel_name = snippet.get("channelTitle", "")
            published_at_str = snippet.get("publishedAt", "")
            tags = snippet.get("tags", [])

            # Parse published_at (ISO 8601 timestamp)
            published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))

            # Extract thumbnail URL (prefer maxresdefault > high > medium > default)
            thumbnails = snippet.get("thumbnails", {})
            thumbnail_url = None
            for quality in ["maxres", "high", "medium", "default"]:
                if quality in thumbnails:
                    thumbnail_url = thumbnails[quality].get("url")
                    break

            # Parse duration using existing method
            duration_str = content_details.get("duration")
            duration_seconds = self._parse_duration(duration_str)

            # Parse statistics (all are strings in YouTube API)
            view_count = int(statistics.get("viewCount", "0"))
            like_count = int(statistics.get("likeCount", "0"))
            comment_count = int(statistics.get("commentCount", "0"))

            return ScrapedYouTubeVideo(
                # Core ScrapedArticle fields
                title=title,
                url=f"https://youtube.com/watch?v={video_id}",
                source_type="youtube_trending",
                external_id=video_id,
                content=description,
                author=channel_name,
                published_at=published_at,
                tags=tags,
                upvotes=like_count,
                comments_count=comment_count,
                raw_data=video_data,
                # YouTube-specific fields
                video_id=video_id,
                channel_id=channel_id,
                channel_name=channel_name,
                thumbnail_url=thumbnail_url,
                duration_seconds=duration_seconds,
                view_count=view_count,
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse trending video: {e}")
            return None

    async def scrape(self, config: dict, keywords: list[str]) -> list[ScrapedYouTubeVideo]:
        """
        Fetch trending videos from tech categories

        Args:
            config: {'category_ids': [28, 27], 'max_results': 50}
            keywords: Filter by keywords in title/description

        Returns:
            List of trending video articles
        """
        # Check quota before proceeding
        if self.quota_manager and not await self.quota_manager.check_quota():
            self.logger.warning("YouTube API quota exhausted, skipping trending")
            return []

        # Implementation in next task
        return []
