import pytest
import httpx
from app.scrapers.strategies.retry import RetryStrategy, MaxRetriesExceeded


@pytest.mark.asyncio
async def test_retry_succeeds_on_first_attempt():
    strategy = RetryStrategy(max_retries=3)

    async def succeeding_task():
        return "success"

    result = await strategy.execute(succeeding_task)
    assert result == "success"


@pytest.mark.asyncio
async def test_retry_succeeds_after_failures():
    strategy = RetryStrategy(max_retries=3, backoff_factor=0.1)
    attempts = []

    async def failing_then_succeeding():
        attempts.append(1)
        if len(attempts) < 3:
            raise httpx.HTTPError("Temporary error")
        return "success"

    result = await strategy.execute(failing_then_succeeding)
    assert result == "success"
    assert len(attempts) == 3


@pytest.mark.asyncio
async def test_retry_exhausts_retries():
    strategy = RetryStrategy(max_retries=2, backoff_factor=0.1)

    async def always_failing():
        raise httpx.HTTPError("Permanent error")

    with pytest.raises(MaxRetriesExceeded):
        await strategy.execute(always_failing)
