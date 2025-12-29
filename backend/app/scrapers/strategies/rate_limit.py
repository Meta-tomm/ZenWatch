import asyncio
import time
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter.

    Args:
        requests_per_minute: Nombre de requêtes autorisées par minute
    """

    def __init__(self, requests_per_minute: int = 60):
        self.rate = requests_per_minute
        self.tokens = float(requests_per_minute)
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        async with self.lock:
            await self._wait_for_token()
            self.tokens -= 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def _wait_for_token(self):
        """Attend qu'un token soit disponible"""
        while self.tokens < 1:
            await asyncio.sleep(0.1)
            self._refill_tokens()

    def _refill_tokens(self):
        """Remplit les tokens basé sur le temps écoulé"""
        now = time.time()
        elapsed = now - self.last_update
        # Ajouter tokens basé sur le taux (rate/60 tokens par seconde)
        self.tokens = min(self.rate, self.tokens + (elapsed * self.rate / 60))
        self.last_update = now
