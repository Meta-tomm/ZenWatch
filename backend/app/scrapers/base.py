from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import httpx


class ScraperPlugin(ABC):
    """Interface de base pour tous les scrapers"""

    name: str
    display_name: str
    version: str

    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None

    @abstractmethod
    async def scrape(self, config: Dict, keywords: List[str]) -> List[Dict]:
        """
        Scrape articles depuis la source.

        Args:
            config: Configuration spécifique au scraper (depuis DB)
            keywords: Liste des mots-clés pour filtrage

        Returns:
            Liste de dictionnaires représentant les articles
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict) -> bool:
        """
        Valide la configuration du scraper.

        Args:
            config: Configuration à valider

        Returns:
            True si valide, False sinon
        """
        pass

    async def _quick_match(self, title: str, keywords: List[str]) -> bool:
        """
        Quick keyword match sur le titre.

        Args:
            title: Titre de l'article
            keywords: Liste des mots-clés

        Returns:
            True si au moins un keyword est présent
        """
        title_lower = title.lower()
        return any(kw.lower() in title_lower for kw in keywords)

    async def __aenter__(self):
        """Context manager pour httpx.AsyncClient"""
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ferme le client HTTP"""
        if self.client:
            await self.client.aclose()
