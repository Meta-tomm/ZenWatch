from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import Optional, List
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Article, Source
from app.schemas.article import ArticleResponse, PaginatedArticlesResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/articles", response_model=PaginatedArticlesResponse)
async def get_articles(
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    sources: Optional[str] = Query(None, description="Comma-separated source types"),
    search: Optional[str] = Query(None, description="Search in title, content, author"),
    sort: str = Query("score", pattern="^(score|date|popularity)$"),
    timeRange: Optional[str] = Query(None, pattern="^(24h|7d|30d)$", description="Time filter"),
    minScore: float = Query(0.0, ge=0.0, le=100.0),
    is_read: Optional[bool] = None,
    is_favorite: Optional[bool] = None,
    is_archived: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Récupère les articles avec filtres et pagination

    - **categories**: Filtrer par catégories (comma-separated: healthtech,web3,dev)
    - **sources**: Filtrer par sources (comma-separated: hackernews,devto)
    - **search**: Recherche dans titre, contenu, auteur, tags
    - **sort**: Trier par (score, date, popularity)
    - **minScore**: Score minimum (0-100)
    - **is_read**: Filtrer par statut lu/non-lu
    - **is_favorite**: Filtrer par favoris
    - **is_archived**: Inclure les articles archivés (False par défaut)
    - **limit**: Nombre max de résultats (1-200)
    - **offset**: Offset pour pagination
    """
    # Eagerly load source relationship to populate source_type
    query = db.query(Article).options(joinedload(Article.source)).filter(
        Article.is_archived == is_archived,
        or_(Article.score >= minScore, Article.score.is_(None))
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

    # Filter by categories (multiple)
    if categories:
        category_list = [c.strip() for c in categories.split(',') if c.strip()]
        if category_list:
            query = query.filter(Article.category.in_(category_list))

    # Filter by sources (multiple) - requires join
    if sources:
        source_list = [s.strip() for s in sources.split(',') if s.strip()]
        if source_list:
            query = query.join(Article.source).filter(Source.type.in_(source_list))

    # Search functionality
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.content.ilike(search_term),
                Article.author.ilike(search_term)
            )
        )

    # Other filters
    if is_read is not None:
        query = query.filter(Article.is_read == is_read)

    if is_favorite is not None:
        query = query.filter(Article.is_favorite == is_favorite)

    # Get total count
    total = query.count()

    # Sorting - map frontend values to backend fields
    if sort == "score":
        query = query.order_by(Article.score.desc())
    elif sort == "date":
        query = query.order_by(Article.published_at.desc())
    elif sort == "popularity":
        # Popularity = upvotes + comments
        query = query.order_by((Article.upvotes + Article.comments_count).desc())

    articles = query.limit(limit).offset(offset).all()

    # Populate source_type from relationship
    articles_data = []
    for article in articles:
        article_dict = {
            **article.__dict__,
            'source_type': article.source.type if article.source else None
        }
        articles_data.append(ArticleResponse.model_validate(article_dict))

    logger.info(
        f"Retrieved {len(articles)} articles "
        f"(filters: categories={categories}, sources={sources}, search={search})"
    )

    return PaginatedArticlesResponse(
        data=articles_data,
        total=total,
        hasMore=offset + len(articles) < total,
        offset=offset,
        limit=limit
    )


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Récupère un article par son ID"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article


@router.patch("/articles/{article_id}/read")
async def mark_as_read(
    article_id: int,
    is_read: bool = True,
    db: Session = Depends(get_db)
):
    """Marque un article comme lu/non-lu"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.is_read = is_read
    db.commit()
    db.refresh(article)

    logger.info(f"Article {article_id} marked as {'read' if is_read else 'unread'}")
    return {"message": "Article updated", "is_read": is_read}


@router.patch("/articles/{article_id}/favorite")
async def toggle_favorite(
    article_id: int,
    is_favorite: bool = True,
    db: Session = Depends(get_db)
):
    """Toggle favori sur un article"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.is_favorite = is_favorite
    db.commit()
    db.refresh(article)

    logger.info(f"Article {article_id} favorite: {is_favorite}")
    return {"message": "Article updated", "is_favorite": is_favorite}


@router.patch("/articles/{article_id}/archive")
async def toggle_archive(
    article_id: int,
    is_archived: bool = True,
    db: Session = Depends(get_db)
):
    """Archive/désarchive un article"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.is_archived = is_archived
    db.commit()
    db.refresh(article)

    logger.info(f"Article {article_id} archived: {is_archived}")
    return {"message": "Article updated", "is_archived": is_archived}


@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Supprime un article"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()

    logger.info(f"Article {article_id} deleted")
    return {"message": "Article deleted"}


@router.get("/articles/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """Récupère la liste des catégories disponibles"""
    categories = db.query(Article.category).distinct().filter(
        Article.category.isnot(None)
    ).all()

    category_list = [cat[0] for cat in categories if cat[0]]

    return {"categories": sorted(category_list)}
