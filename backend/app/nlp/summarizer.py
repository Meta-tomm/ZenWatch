"""
Article Summarizer - Claude AI-based summarization
Génère des résumés concis des articles via l'API Anthropic Claude
"""

from typing import Optional
import anthropic
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ArticleSummarizer:
    """Génère des résumés IA des articles via Claude API"""

    def __init__(self):
        """Initialize Claude client"""
        if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "sk-ant-your-api-key-here":
            logger.warning("Anthropic API key not configured - summarization disabled")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info("Claude AI client initialized")

    async def summarize(
        self,
        title: str,
        content: Optional[str],
        max_length: int = 200
    ) -> Optional[str]:
        """
        Génère un résumé concis de l'article

        Args:
            title: Titre de l'article
            content: Contenu de l'article (peut être None)
            max_length: Longueur max du résumé en mots

        Returns:
            Résumé généré ou None si erreur/pas de contenu
        """
        if not self.client:
            logger.debug("Summarization skipped - API key not configured")
            return None

        if not content or len(content.strip()) < 50:
            logger.debug(f"Content too short to summarize: {title}")
            return None

        try:
            # Truncate content si trop long (limite API Claude)
            max_content_length = 8000  # chars
            truncated_content = content[:max_content_length]

            prompt = f"""Résume l'article suivant de manière concise et factuelle en MAXIMUM {max_length} mots.
Concentre-toi sur les points clés et les informations importantes.

Titre: {title}

Contenu:
{truncated_content}

Résumé (max {max_length} mots):"""

            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.3,  # Plus déterministe
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = message.content[0].text.strip()

            logger.info(f"Generated summary for: {title[:50]}... (length: {len(summary.split())} words)")
            return summary

        except anthropic.APIError as e:
            logger.error(f"Claude API error during summarization: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during summarization: {e}")
            return None

    def summarize_sync(
        self,
        title: str,
        content: Optional[str],
        max_length: int = 200
    ) -> Optional[str]:
        """
        Génère un résumé concis de l'article (version synchrone pour Celery)

        Args:
            title: Titre de l'article
            content: Contenu de l'article (peut être None)
            max_length: Longueur max du résumé en mots

        Returns:
            Résumé généré ou None si erreur/pas de contenu
        """
        if not self.client:
            logger.debug("Summarization skipped - API key not configured")
            return None

        if not content or len(content.strip()) < 50:
            logger.debug(f"Content too short to summarize: {title}")
            return None

        try:
            # Truncate content si trop long (limite API Claude)
            max_content_length = 8000  # chars
            truncated_content = content[:max_content_length]

            prompt = f"""Résume l'article suivant de manière concise et factuelle en MAXIMUM {max_length} mots.
Concentre-toi sur les points clés et les informations importantes.

Titre: {title}

Contenu:
{truncated_content}

Résumé (max {max_length} mots):"""

            # Synchronous call - Anthropic SDK is synchronous
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.3,  # Plus déterministe
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = message.content[0].text.strip()

            logger.info(f"Generated summary for: {title[:50]}... (length: {len(summary.split())} words)")
            return summary

        except anthropic.APIError as e:
            logger.error(f"Claude API error during summarization: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during summarization: {e}")
            return None

    async def summarize_batch(
        self,
        articles: list[dict],
        max_length: int = 200
    ) -> dict[str, Optional[str]]:
        """
        Génère des résumés pour plusieurs articles

        Args:
            articles: Liste de dicts {"id": str, "title": str, "content": str}
            max_length: Longueur max par résumé

        Returns:
            Dict {article_id: summary}
        """
        summaries = {}

        for article in articles:
            article_id = article.get("id")
            title = article.get("title", "")
            content = article.get("content")

            if not article_id:
                continue

            summary = await self.summarize(title, content, max_length)
            summaries[article_id] = summary

        logger.info(f"Batch summarization complete: {len(summaries)} summaries generated")
        return summaries
