from datetime import datetime
from typing import Any

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
    SHORTS_THRESHOLD_SECONDS = 60  # Videos under this duration are considered YouTube Shorts

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

    def _parse_trending_video(self, video_data: dict[str, Any]) -> ScrapedYouTubeVideo | None:
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

    def _fetch_trending_videos(
        self,
        region_code: str = "US",
        max_results: int = 50,
        video_category: str = "28"
    ) -> list[dict[str, Any]]:
        """
        Fetch trending videos from YouTube Data API v3.

        Args:
            region_code: Geographic region code (e.g., "US", "FR")
            max_results: Maximum number of results (1-50)
            video_category: Category ID ("28" for Science & Technology)

        Returns:
            List of raw video data dicts from YouTube API
            Returns empty list on error (never raises)
        """
        import time

        from googleapiclient.errors import HttpError

        if not self.youtube:
            self.logger.error("YouTube client not initialized (API key missing)")
            return []

        retry_count = 0

        while retry_count <= self.MAX_RETRIES:
            try:
                # Call YouTube Data API v3 videos.list endpoint
                response = self.youtube.videos().list(
                    part='snippet,contentDetails,statistics',
                    chart='mostPopular',
                    videoCategoryId=video_category,
                    regionCode=region_code,
                    maxResults=max_results
                ).execute()

                # Extract items from response
                items = response.get("items", [])
                self.logger.info(
                    f"Fetched {len(items)} trending videos from YouTube API "
                    f"(region={region_code}, category={video_category})"
                )
                return items

            except HttpError as e:
                # Handle rate limiting (429) with exponential backoff
                if e.resp.status == 429:
                    if retry_count < self.MAX_RETRIES:
                        # Exponential backoff: 2^(retry_count + 1) seconds
                        delay = 2 ** (retry_count + 1)
                        self.logger.warning(
                            f"Rate limit hit (429), retrying in {delay}s "
                            f"(attempt {retry_count + 1}/{self.MAX_RETRIES})"
                        )
                        time.sleep(delay)
                        retry_count += 1
                        continue
                    else:
                        self.logger.error(
                            f"Rate limit exceeded after {self.MAX_RETRIES} retries, giving up"
                        )
                        return []

                # Handle forbidden (403) - API key invalid or quota exceeded
                elif e.resp.status == 403:
                    self.logger.error(f"YouTube API forbidden (403): {e}")
                    return []

                # Other HTTP errors
                else:
                    self.logger.error(f"YouTube API HTTP error ({e.resp.status}): {e}")
                    return []

            except Exception as e:
                # Catch-all for network errors, timeouts, etc.
                self.logger.error(f"Unexpected error fetching trending videos: {e}")
                return []

        # Should never reach here, but return empty list as safety
        return []

    def _filter_by_keywords(
        self,
        videos: list[ScrapedYouTubeVideo],
        keywords: list[dict[str, Any]],
        config: dict[str, Any] | None = None
    ) -> list[ScrapedYouTubeVideo]:
        """
        Filter videos by keywords and calculate relevance scores.

        Args:
            videos: List of scraped YouTube videos
            keywords: List of keyword dicts with structure:
                [{"keyword": "rust", "weight": 5.0, "category": "programming"}, ...]
            config: Optional configuration dict:
                {
                    "min_keyword_matches": 1,  # Minimum keywords required to match
                    "include_shorts": False,   # Exclude videos < 60 seconds
                    "min_view_count": 1000     # Minimum views threshold
                }

        Returns:
            Filtered list of videos with updated scores, sorted by score (highest first)
        """
        if not videos or not keywords:
            return []

        # Parse config with defaults
        config = config or {}
        min_keyword_matches = config.get("min_keyword_matches", 1)
        include_shorts = config.get("include_shorts", True)
        min_view_count = config.get("min_view_count", 0)

        filtered_videos = []

        for video in videos:
            # Build searchable text: title + description + tags (case-insensitive)
            searchable_text = (
                f"{video.title} {video.content or ''} {' '.join(video.tags or [])}"
            ).lower()

            # Calculate relevance score by matching keywords
            relevance_score = 0.0
            matched_keywords = 0

            for keyword_data in keywords:
                keyword = keyword_data.get("keyword", "")
                if not isinstance(keyword, str):
                    self.logger.warning(f"Invalid keyword type: {type(keyword)}, skipping")
                    continue

                keyword = keyword.lower()
                weight = keyword_data.get("weight", 1.0)

                # Case-insensitive substring match
                if keyword and keyword in searchable_text:
                    relevance_score += weight
                    matched_keywords += 1

            # Skip if below minimum keyword matches threshold
            if matched_keywords < min_keyword_matches:
                continue

            # Skip if below view count threshold (treat None as 0)
            if (video.view_count or 0) < min_view_count:
                continue

            # Skip shorts if include_shorts=False
            if not include_shorts and video.duration_seconds and video.duration_seconds < self.SHORTS_THRESHOLD_SECONDS:
                continue

            # Store score in raw_data and attach as dynamic attribute
            # Pydantic allows setting arbitrary attributes if not in __fields__
            updated_raw_data = {**video.raw_data, "relevance_score": relevance_score}
            video_copy = video.model_copy(update={"raw_data": updated_raw_data})

            # Use object.__setattr__ to bypass Pydantic's validation for dynamic attribute
            object.__setattr__(video_copy, 'score', relevance_score)
            filtered_videos.append(video_copy)

        # Sort by score (highest first)
        filtered_videos.sort(key=lambda v: v.score, reverse=True)

        self.logger.info(
            f"Filtered {len(videos)} videos to {len(filtered_videos)} "
            f"(matched {len(filtered_videos)} with keywords)"
        )

        return filtered_videos

    async def scrape(
        self,
        config: dict[str, Any],
        keywords: list[dict[str, Any]]
    ) -> list[ScrapedYouTubeVideo]:
        """
        Scrape trending YouTube videos filtered by keywords

        Args:
            config: Scraper configuration (region_code, max_results, etc.)
            keywords: List of keyword dicts with 'keyword', 'weight', 'category'

        Returns:
            List of filtered ScrapedYouTubeVideo objects sorted by relevance
        """
        # Check quota availability BEFORE making API call
        if self.quota_manager and not await self.quota_manager.check_quota():
            self.logger.warning("YouTube API quota exhausted, skipping trending scrape")
            return []

        # Extract config values with defaults
        region_code = config.get("region_code", "US")
        max_results = config.get("max_results", 50)
        video_category = config.get("video_category", "28")

        # Fetch trending videos from YouTube API
        raw_videos = self._fetch_trending_videos(
            region_code=region_code,
            max_results=max_results,
            video_category=video_category
        )

        # Record quota usage AFTER successful API call (100 units per call)
        if self.quota_manager:
            await self.quota_manager.record_usage(100)

        # Parse raw video data into ScrapedYouTubeVideo objects
        # Filter out parsing failures (None values)
        videos = [
            parsed_video
            for raw_video in raw_videos
            if (parsed_video := self._parse_trending_video(raw_video)) is not None
        ]

        self.logger.info(f"Parsed {len(videos)} videos from {len(raw_videos)} raw items")

        # Filter by keywords and calculate relevance scores
        filtered_videos = self._filter_by_keywords(videos, keywords, config)

        self.logger.info(
            f"Scraped {len(filtered_videos)} relevant trending videos "
            f"from {len(videos)} total (region={region_code})"
        )

        return filtered_videos
