from datetime import datetime, UTC
import redis.asyncio as redis
from app.utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeQuotaManager:
    """Track and enforce YouTube API quota limits"""

    DAILY_LIMIT = 10000  # Free tier
    WARNING_THRESHOLD = 9500  # 95%

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def _get_quota_key(self) -> str:
        """Redis key for today's quota"""
        today = datetime.now(UTC).strftime('%Y-%m-%d')
        return f"youtube_api_quota:{today}"

    async def check_quota(self) -> bool:
        """Check if quota is available"""
        key = self._get_quota_key()
        usage = await self.redis.get(key)

        if usage is None:
            return True

        current_usage = int(usage)

        if current_usage >= self.WARNING_THRESHOLD:
            logger.warning(f"YouTube quota at {current_usage}/{self.DAILY_LIMIT}")

        return current_usage < self.DAILY_LIMIT

    async def record_usage(self, units: int):
        """Record quota usage"""
        key = self._get_quota_key()
        await self.redis.incrby(key, units)
        await self.redis.expire(key, 86400 * 2)  # Keep for 2 days

    async def get_usage(self) -> int:
        """Get current day's usage"""
        key = self._get_quota_key()
        usage = await self.redis.get(key)
        return int(usage) if usage else 0
