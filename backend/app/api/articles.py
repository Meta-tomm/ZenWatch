from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import Article
from app.schemas.article import ArticleResponse, PaginatedArticlesResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/articles", response_model=PaginatedArticlesResponse)
async def get_articles(
    category: Optional[str] = None,
    source_type: Optional[str] = None,
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    is_read: Optional[bool] = None,
    is_favorite: Optional[bool] = None,
    is_archived: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("score", pattern="^(score|published_at|created_at)$"),
    db: Session = Depends(get_db)
):
    """
    Récupère les articles avec filtres et pagination

    - **category**: Filtrer par catégorie (healthtech, web3, dev, etc.)
    - **source_type**: Filtrer par source (reddit, hackernews, etc.)
    - **min_score**: Score minimum (0-100)
    - **is_read**: Filtrer par statut lu/non-lu
    - **is_favorite**: Filtrer par favoris
    - **is_archived**: Inclure les articles archivés (False par défaut)
    - **limit**: Nombre max de résultats (1-200)
    - **offset**: Offset pour pagination
    - **sort_by**: Trier par (score, published_at, created_at)
    """
    query = db.query(Article).filter(
        Article.is_archived == is_archived,
        Article.score >= min_score
    )

    if category:
        query = query.filter(Article.category == category)

    if source_type:
        query = query.filter(Article.source_type == source_type)

    if is_read is not None:
        query = query.filter(Article.is_read == is_read)

    if is_favorite is not None:
        query = query.filter(Article.is_favorite == is_favorite)

    # Get total count
    total = query.count()

    # Sorting
    if sort_by == "score":
        query = query.order_by(Article.score.desc())
    elif sort_by == "published_at":
        query = query.order_by(Article.published_at.desc())
    else:  # created_at
        query = query.order_by(Article.created_at.desc())

    articles = query.limit(limit).offset(offset).all()

    logger.info(f"Retrieved {len(articles)} articles (filters: category={category}, source={source_type})")

    return PaginatedArticlesResponse(
        data=articles,
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
