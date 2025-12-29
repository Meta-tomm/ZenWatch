import asyncio
import random
from typing import Callable, Awaitable, TypeVar
import httpx
from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class MaxRetriesExceeded(Exception):
    """Exception levée quand max retries atteint"""
    pass


class RetryStrategy:
    """
    Retry avec backoff exponentiel + jitter.

    Args:
        max_retries: Nombre max de tentatives
        backoff_factor: Facteur de backoff exponentiel
    """

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def execute(self, func: Callable[[], Awaitable[T]]) -> T:
        """
        Exécute la fonction async avec retry logic.

        Args:
            func: Fonction async à exécuter (callable qui retourne une coroutine)

        Returns:
            Résultat de la fonction

        Raises:
            MaxRetriesExceeded: Si max retries atteint
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return await func()
            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                last_exception = e

                if attempt < self.max_retries - 1:
                    # Backoff exponentiel avec jitter
                    wait_time = (self.backoff_factor ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"Retry {attempt + 1}/{self.max_retries} after {wait_time:.2f}s. Error: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Max retries ({self.max_retries}) exceeded. Last error: {e}")

        raise MaxRetriesExceeded(
            f"Failed after {self.max_retries} retries"
        ) from last_exception
