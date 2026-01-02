from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Keyword
from app.schemas.keyword import (
    KeywordCreate,
    KeywordUpdate,
    KeywordResponse,
    KeywordListResponse
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/keywords", response_model=KeywordListResponse)
async def get_keywords(
    category: str = Query(None),
    is_active: bool = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Récupère les mots-clés avec filtres

    - **category**: Filtrer par catégorie
    - **is_active**: Filtrer par statut actif/inactif
    - **limit**: Nombre max de résultats
    - **offset**: Offset pour pagination
    """
    query = db.query(Keyword)

    if category:
        query = query.filter(Keyword.category == category)

    if is_active is not None:
        query = query.filter(Keyword.is_active == is_active)

    total = query.count()
    keywords = query.order_by(Keyword.weight.desc()).limit(limit).offset(offset).all()

    logger.info(f"Retrieved {len(keywords)} keywords (total: {total})")
    return KeywordListResponse(keywords=keywords, total=total)


@router.get("/keywords/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int,
    db: Session = Depends(get_db)
):
    """Récupère un mot-clé par son ID"""
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    return keyword


@router.post("/keywords", response_model=KeywordResponse, status_code=201)
async def create_keyword(
    keyword_data: KeywordCreate,
    db: Session = Depends(get_db)
):
    """Crée un nouveau mot-clé"""
    # Check if keyword already exists
    existing = db.query(Keyword).filter(
        Keyword.keyword == keyword_data.keyword
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Keyword '{keyword_data.keyword}' already exists"
        )

    keyword = Keyword(**keyword_data.model_dump())
    db.add(keyword)
    db.commit()
    db.refresh(keyword)

    logger.info(f"Keyword created: {keyword.keyword} (category: {keyword.category}, weight: {keyword.weight})")
    return keyword


@router.patch("/keywords/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    keyword_data: KeywordUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un mot-clé"""
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    # Update fields
    update_data = keyword_data.model_dump(exclude_unset=True)

    # Check uniqueness if keyword is being changed
    if "keyword" in update_data:
        existing = db.query(Keyword).filter(
            Keyword.keyword == update_data["keyword"],
            Keyword.id != keyword_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Keyword '{update_data['keyword']}' already exists"
            )

    for field, value in update_data.items():
        setattr(keyword, field, value)

    db.commit()
    db.refresh(keyword)

    logger.info(f"Keyword {keyword_id} updated: {keyword.keyword}")
    return keyword


@router.delete("/keywords/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: Session = Depends(get_db)
):
    """Supprime un mot-clé"""
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    keyword_name = keyword.keyword
    db.delete(keyword)
    db.commit()

    logger.info(f"Keyword deleted: {keyword_name}")
    return {"message": f"Keyword '{keyword_name}' deleted"}


@router.get("/keywords/categories/list")
async def get_keyword_categories(db: Session = Depends(get_db)):
    """Récupère la liste des catégories de mots-clés"""
    categories = db.query(Keyword.category).distinct().filter(
        Keyword.category.isnot(None)
    ).all()

    category_list = [cat[0] for cat in categories if cat[0]]

    return {"categories": sorted(category_list)}
