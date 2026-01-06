from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import Article, Source
from app.schemas.article import ArticleResponse
from app.utils.logger import get_logger
from pydantic import BaseModel
import random

logger = get_logger(__name__)
router = APIRouter()


class TriageResponse(BaseModel):
    items: list[ArticleResponse]
    remaining_count: int


@router.get("/triage", response_model=TriageResponse)
async def get_triage_items(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get items for triage (swipe interface).

    Algorithm:
    - Exclude: is_bookmarked, is_dismissed, is_archived
    - 70% high-score articles (score >= 50)
    - 30% discovery articles (score < 50 or null)
    - Randomized within each group
    """
    # Base query: exclude already processed items
    base_query = db.query(Article).options(joinedload(Article.source)).filter(
        Article.is_bookmarked == False,
        Article.is_dismissed == False,
        Article.is_archived == False
    )

    # Get remaining count for UI
    remaining_count = base_query.count()

    # Split into high-score and discovery
    high_score_count = int(limit * 0.7)
    discovery_count = limit - high_score_count

    # High score items (score >= 50)
    high_score_items = base_query.filter(
        Article.score >= 50
    ).order_by(func.random()).limit(high_score_count).all()

    # Discovery items (score < 50 or null)
    discovery_items = base_query.filter(
        (Article.score < 50) | (Article.score.is_(None))
    ).order_by(func.random()).limit(discovery_count).all()

    # Combine and shuffle
    all_items = high_score_items + discovery_items
    random.shuffle(all_items)

    # Transform to response
    items_data = []
    for item in all_items:
        item_dict = {
            **item.__dict__,
            'source_type': item.source.type if item.source else None
        }
        items_data.append(ArticleResponse.model_validate(item_dict))

    logger.info(f"Retrieved {len(items_data)} triage items (remaining: {remaining_count})")

    return TriageResponse(
        items=items_data,
        remaining_count=remaining_count
    )


@router.post("/articles/{article_id}/dismiss")
async def dismiss_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Mark an article as dismissed (won't appear in triage)"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.is_dismissed = True
    db.commit()

    logger.info(f"Article {article_id} dismissed from triage")

    return {"success": True, "message": "Article dismissed"}
