import pytest
import asyncio
import time
from app.scrapers.strategies.rate_limit import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests():
    limiter = RateLimiter(requests_per_minute=120)  # 2 req/sec

    start = time.time()
    async with limiter:
        pass
    async with limiter:
        pass
    elapsed = time.time() - start

    assert elapsed < 1.0  # Should be fast for 2 requests


@pytest.mark.asyncio
async def test_rate_limiter_throttles():
    # Start with minimal tokens
    limiter = RateLimiter(requests_per_minute=60)
    limiter.tokens = 1  # Force to have only 1 token

    timestamps = []

    async def make_request():
        async with limiter:
            timestamps.append(time.time())

    # Make 2 requests - first should be immediate, second should wait
    start = time.time()
    await asyncio.gather(make_request(), make_request())
    elapsed = time.time() - start

    # With 1 initial token and 60 req/min (1 req/sec),
    # the second request should wait ~1 second
    assert elapsed >= 0.9  # Allow small margin
    assert len(timestamps) == 2
