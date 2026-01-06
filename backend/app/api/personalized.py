"""
Personalized feed endpoints.

Returns articles with user-specific scores based on their keywords.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.auth.deps import get_current_user
from app.database import get_db
from app.models import Article, Source
from app.models.user import User
from app.models.user_keyword import UserKeyword
from app.models.user_article_score import UserArticleScore
from app.schemas.article import ArticleResponse
from app.services.user_scoring import UserScoringService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/personalized", tags=["personalized"])


class PersonalizedArticleResponse(ArticleResponse):
    """Article with personalized score."""
    personalized_score: Optional[float] = None
    keyword_matches: Optional[int] = None


class PersonalizedFeedResponse(BaseModel):
    """Response for personalized feed."""
    data: list[PersonalizedArticleResponse]
    total: int
    hasMore: bool
    offset: int
    limit: int


@router.get("/feed", response_model=PersonalizedFeedResponse)
async def get_personalized_feed(
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    sources: Optional[str] = Query(None, description="Comma-separated source types"),
    search: Optional[str] = Query(None, description="Search in title, content"),
    timeRange: Optional[str] = Query(None, pattern="^(24h|7d|30d)$"),
    minScore: float = Query(0.0, ge=0.0, le=100.0),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized article feed sorted by user's keyword-based scores.

    Returns articles ordered by personalized_score, with scores calculated
    based on the user's configured keywords and weights.
    """
    # Check if user has keywords
    has_keywords = db.query(UserKeyword).filter(
        UserKeyword.user_id == user.id,
        UserKeyword.is_active == True
    ).first() is not None

    # Base query with eager loading
    query = db.query(Article).options(joinedload(Article.source)).filter(
        Article.is_archived == False
    )

    # Time range filter
    if timeRange:
        if timeRange == "24h":
            since = datetime.utcnow() - timedelta(hours=24)
        elif timeRange == "7d":
            since = datetime.utcnow() - timedelta(days=7)
        elif timeRange == "30d":
            since = datetime.utcnow() - timedelta(days=30)
        query = query.filter(Article.published_at >= since)

    # Filter by categories
    if categories:
        category_list = [c.strip() for c in categories.split(',') if c.strip()]
        if category_list:
            query = query.filter(Article.category.in_(category_list))

    # Filter by sources
    if sources:
        source_list = [s.strip() for s in sources.split(',') if s.strip()]
        if source_list:
            query = query.join(Article.source).filter(Source.type.in_(source_list))

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.content.ilike(search_term),
                Article.author.ilike(search_term)
            )
        )

    if has_keywords:
        # Join with user scores and order by personalized score
        query = query.outerjoin(
            UserArticleScore,
            (UserArticleScore.article_id == Article.id) &
            (UserArticleScore.user_id == user.id)
        )

        # Filter by min personalized score
        if minScore > 0:
            query = query.filter(
                or_(
                    UserArticleScore.score >= minScore,
                    UserArticleScore.score.is_(None)
                )
            )

        # Order by personalized score, then global score
        query = query.order_by(
            func.coalesce(UserArticleScore.score, Article.score, 0).desc(),
            Article.published_at.desc()
        )
    else:
        # No keywords - use global score
        if minScore > 0:
            query = query.filter(
                or_(Article.score >= minScore, Article.score.is_(None))
            )
        query = query.order_by(Article.score.desc(), Article.published_at.desc())

    # Get total count
    total = query.count()

    # Apply pagination
    articles = query.limit(limit).offset(offset).all()

    # Build response with personalized scores
    articles_data = []
    for article in articles:
        # Get personalized score if exists
        user_score = db.query(UserArticleScore).filter(
            UserArticleScore.user_id == user.id,
            UserArticleScore.article_id == article.id
        ).first()

        article_dict = {
            **article.__dict__,
            'source_type': article.source.type if article.source else None,
            'personalized_score': user_score.score if user_score else None,
            'keyword_matches': user_score.keyword_matches if user_score else None
        }
        articles_data.append(PersonalizedArticleResponse.model_validate(article_dict))

    logger.info(
        f"Retrieved {len(articles)} personalized articles for user {user.id} "
        f"(has_keywords={has_keywords})"
    )

    return PersonalizedFeedResponse(
        data=articles_data,
        total=total,
        hasMore=offset + len(articles) < total,
        offset=offset,
        limit=limit
    )


@router.post("/score-new")
async def score_new_articles(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Score any unscored articles for the current user.
    Called periodically or after new scraping.
    """
    scoring_service = UserScoringService(db)
    count = scoring_service.score_articles_for_user(user.id)

    logger.info(f"Scored {count} new articles for user {user.id}")
    return {"message": f"Scored {count} articles", "count": count}


@router.get("/stats")
async def get_personalized_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about user's personalized scoring.
    """
    # Count keywords
    keyword_count = db.query(UserKeyword).filter(
        UserKeyword.user_id == user.id,
        UserKeyword.is_active == True
    ).count()

    # Count scored articles
    scored_count = db.query(UserArticleScore).filter(
        UserArticleScore.user_id == user.id
    ).count()

    # Average personalized score
    avg_score = db.query(func.avg(UserArticleScore.score)).filter(
        UserArticleScore.user_id == user.id
    ).scalar() or 0.0

    # High score articles (>70)
    high_score_count = db.query(UserArticleScore).filter(
        UserArticleScore.user_id == user.id,
        UserArticleScore.score >= 70
    ).count()

    return {
        "keyword_count": keyword_count,
        "scored_articles": scored_count,
        "average_score": round(avg_score, 1),
        "high_relevance_count": high_score_count
    }
