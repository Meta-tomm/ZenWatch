from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models import Article, Source
from app.schemas.article import ArticleResponse
from app.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)
router = APIRouter()


class LibraryResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    unread_count: int


@router.get("/library", response_model=LibraryResponse)
async def get_library(
    type: Optional[str] = Query(None, pattern="^(all|article|video)$"),
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all bookmarked items (Library)"""
    query = db.query(Article).options(joinedload(Article.source)).filter(
        Article.is_bookmarked == True
    )

    # Filter by type
    if type == "article":
        query = query.filter(Article.is_video == False)
    elif type == "video":
        query = query.filter(Article.is_video == True)

    # Filter unread only
    if unread_only:
        query = query.filter(Article.is_read == False)

    # Get total count before filtering unread
    base_count_query = db.query(Article).filter(Article.is_bookmarked == True)
    if type == "article":
        base_count_query = base_count_query.filter(Article.is_video == False)
    elif type == "video":
        base_count_query = base_count_query.filter(Article.is_video == True)

    total = base_count_query.count()
    unread_count = base_count_query.filter(Article.is_read == False).count()

    # Sort by bookmarked_at descending (newest first)
    items = query.order_by(Article.bookmarked_at.desc()).limit(limit).offset(offset).all()

    # Transform to response
    items_data = []
    for item in items:
        item_dict = {
            **item.__dict__,
            'source_type': item.source.type if item.source else None
        }
        items_data.append(ArticleResponse.model_validate(item_dict))

    logger.info(f"Retrieved {len(items)} library items (total: {total}, unread: {unread_count})")

    return LibraryResponse(
        items=items_data,
        total=total,
        unread_count=unread_count
    )


@router.post("/articles/{article_id}/bookmark", response_model=ArticleResponse)
async def toggle_bookmark(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Toggle bookmark status on an article"""
    article = db.query(Article).options(joinedload(Article.source)).filter(
        Article.id == article_id
    ).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Toggle bookmark
    if article.is_bookmarked:
        article.is_bookmarked = False
        article.bookmarked_at = None
        logger.info(f"Article {article_id} removed from library")
    else:
        article.is_bookmarked = True
        article.bookmarked_at = datetime.utcnow()
        logger.info(f"Article {article_id} added to library")

    db.commit()
    db.refresh(article)

    article_dict = {
        **article.__dict__,
        'source_type': article.source.type if article.source else None
    }
    return ArticleResponse.model_validate(article_dict)
