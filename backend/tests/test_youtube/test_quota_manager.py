import pytest
import redis.asyncio as redis
from datetime import datetime, UTC
from app.youtube.quota_manager import YouTubeQuotaManager

@pytest.mark.asyncio
async def test_quota_manager_tracks_usage(redis_client):
    """Test quota usage tracking"""
    manager = YouTubeQuotaManager(redis_client)

    # Initially should be available
    assert await manager.check_quota() == True

    # Record usage
    await manager.record_usage(100)

    usage = await manager.get_usage()
    assert usage == 100

@pytest.mark.asyncio
async def test_quota_manager_enforces_limit(redis_client):
    """Test quota limit enforcement"""
    manager = YouTubeQuotaManager(redis_client)

    # Use up quota
    await manager.record_usage(10000)

    # Should return False when exhausted
    assert await manager.check_quota() == False

@pytest.mark.asyncio
async def test_quota_manager_daily_reset(redis_client):
    """Test quota key is date-based"""
    manager = YouTubeQuotaManager(redis_client)

    key = manager._get_quota_key()
    today = datetime.now(UTC).strftime('%Y-%m-%d')

    assert today in key
    assert key == f"youtube_api_quota:{today}"
