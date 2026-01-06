"""
Personalized article scoring service.

Calculates relevance scores for articles based on each user's keywords.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.article import Article
from app.models.user_keyword import UserKeyword
from app.models.user_article_score import UserArticleScore
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserScoringService:
    """Service for calculating personalized article scores."""

    def __init__(self, db: Session):
        self.db = db

    def score_article_for_user(
        self,
        article: Article,
        user_id: int,
        user_keywords: Optional[List[UserKeyword]] = None
    ) -> float:
        """
        Calculate personalized score for a single article.

        Args:
            article: Article to score
            user_id: User ID
            user_keywords: Optional pre-fetched keywords (for batch operations)

        Returns:
            Score between 0-100
        """
        # Fetch keywords if not provided
        if user_keywords is None:
            user_keywords = self.db.query(UserKeyword).filter(
                UserKeyword.user_id == user_id,
                UserKeyword.is_active == True
            ).all()

        if not user_keywords:
            # No keywords = use global score
            return article.score or 0.0

        # Build searchable text
        text = f"{article.title or ''} {article.content or ''} {article.summary or ''}".lower()
        tags_text = ' '.join(article.tags or []).lower()
        full_text = f"{text} {tags_text}"

        total_score = 0.0
        total_weight = 0.0
        matches = 0

        for kw in user_keywords:
            keyword_lower = kw.keyword.lower()
            weight = kw.weight or 1.0

            # Check for keyword match
            if keyword_lower in full_text:
                # Boost based on where keyword appears
                boost = 1.0
                if keyword_lower in (article.title or '').lower():
                    boost = 2.0  # Title match is more important
                elif keyword_lower in tags_text:
                    boost = 1.5  # Tag match is also important

                total_score += weight * boost * 20  # Base score per match
                matches += 1

            total_weight += weight

        if matches == 0:
            # No matches - return low score
            return max(0, (article.score or 0) * 0.3)  # 30% of global score

        # Calculate final score
        # Base: weighted average of matches
        # Bonus: more matches = higher score
        match_bonus = min(matches * 5, 25)  # Up to 25 bonus points for multiple matches
        raw_score = (total_score / total_weight) + match_bonus

        # Blend with global score (20% global, 80% personalized)
        global_score = article.score or 50
        final_score = (raw_score * 0.8) + (global_score * 0.2)

        # Clamp to 0-100
        return max(0, min(100, final_score))

    def score_articles_for_user(
        self,
        user_id: int,
        article_ids: Optional[List[int]] = None,
        limit: int = 500
    ) -> int:
        """
        Score multiple articles for a user (batch operation).

        Args:
            user_id: User ID
            article_ids: Optional list of article IDs to score (scores all recent if None)
            limit: Max articles to score

        Returns:
            Number of articles scored
        """
        # Get user's keywords
        user_keywords = self.db.query(UserKeyword).filter(
            UserKeyword.user_id == user_id,
            UserKeyword.is_active == True
        ).all()

        if not user_keywords:
            logger.info(f"User {user_id} has no keywords, skipping scoring")
            return 0

        # Get articles to score
        query = self.db.query(Article)
        if article_ids:
            query = query.filter(Article.id.in_(article_ids))
        else:
            # Score recent articles that don't have a score yet for this user
            scored_ids = self.db.query(UserArticleScore.article_id).filter(
                UserArticleScore.user_id == user_id
            ).subquery()
            query = query.filter(~Article.id.in_(scored_ids))

        articles = query.order_by(Article.published_at.desc()).limit(limit).all()

        scored_count = 0
        for article in articles:
            score = self.score_article_for_user(article, user_id, user_keywords)

            # Upsert score
            existing = self.db.query(UserArticleScore).filter(
                UserArticleScore.user_id == user_id,
                UserArticleScore.article_id == article.id
            ).first()

            if existing:
                existing.score = score
                existing.scored_at = datetime.utcnow()
            else:
                user_score = UserArticleScore(
                    user_id=user_id,
                    article_id=article.id,
                    score=score,
                    keyword_matches=self._count_matches(article, user_keywords)
                )
                self.db.add(user_score)

            scored_count += 1

        self.db.commit()
        logger.info(f"Scored {scored_count} articles for user {user_id}")
        return scored_count

    def rescore_user_articles(self, user_id: int) -> int:
        """
        Rescore all articles for a user (after keyword change).

        Args:
            user_id: User ID

        Returns:
            Number of articles rescored
        """
        # Delete existing scores
        self.db.query(UserArticleScore).filter(
            UserArticleScore.user_id == user_id
        ).delete()
        self.db.commit()

        # Score all articles
        return self.score_articles_for_user(user_id, limit=1000)

    def get_user_score(self, user_id: int, article_id: int) -> Optional[float]:
        """Get a user's score for a specific article."""
        score = self.db.query(UserArticleScore).filter(
            UserArticleScore.user_id == user_id,
            UserArticleScore.article_id == article_id
        ).first()
        return score.score if score else None

    def _count_matches(self, article: Article, keywords: List[UserKeyword]) -> int:
        """Count how many keywords match an article."""
        text = f"{article.title or ''} {article.content or ''} {' '.join(article.tags or [])}".lower()
        return sum(1 for kw in keywords if kw.keyword.lower() in text)


def score_new_articles_for_all_users(db: Session) -> dict:
    """
    Score new articles for all users with keywords.
    Called after scraping completes.

    Returns:
        Dict with stats
    """
    from app.models.user import User

    # Get users with keywords
    users_with_keywords = db.query(User.id).join(UserKeyword).distinct().all()
    user_ids = [u[0] for u in users_with_keywords]

    if not user_ids:
        logger.info("No users with keywords found")
        return {"users": 0, "articles_scored": 0}

    service = UserScoringService(db)
    total_scored = 0

    for user_id in user_ids:
        scored = service.score_articles_for_user(user_id)
        total_scored += scored

    logger.info(f"Scored articles for {len(user_ids)} users, total {total_scored} scores")
    return {
        "users": len(user_ids),
        "articles_scored": total_scored
    }
