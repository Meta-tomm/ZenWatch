from typing import Dict, Type, Optional
from app.scrapers.base import ScraperPlugin
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScraperRegistry:
    """Singleton registry pour tous les scrapers plugins"""

    _instance = None
    _plugins: Dict[str, Type[ScraperPlugin]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, name: str, plugin_class: Type[ScraperPlugin]):
        """Enregistre un plugin scraper"""
        self._plugins[name] = plugin_class
        logger.info(f"Registered scraper plugin: {name}")

    def get(self, name: str) -> Optional[ScraperPlugin]:
        """Récupère une instance du plugin"""
        plugin_class = self._plugins.get(name)
        if plugin_class:
            return plugin_class()
        logger.warning(f"Scraper plugin not found: {name}")
        return None

    def list_plugins(self) -> Dict[str, Type[ScraperPlugin]]:
        """Liste tous les plugins enregistrés"""
        return self._plugins.copy()

    def clear(self):
        """Clear registry (pour tests)"""
        self._plugins.clear()


def scraper_plugin(name: str, display_name: str, version: str, required_config: list = None):
    """
    Décorateur pour auto-registration des scrapers.

    Usage:
        @scraper_plugin(name="reddit", display_name="Reddit", version="1.0.0")
        class RedditScraper(ScraperPlugin):
            ...
    """
    def decorator(cls: Type[ScraperPlugin]):
        # Ajouter métadonnées
        cls.name = name
        cls.display_name = display_name
        cls.version = version
        cls.required_config = required_config or []

        # Auto-register
        registry = ScraperRegistry()
        registry.register(name, cls)

        return cls

    return decorator
