"""User Keywords API routes"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.auth.deps import get_current_user
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Pydantic schemas for user keywords
class UserKeywordCreate(BaseModel):
    """Create user keyword request"""
    keyword: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    weight: float = Field(1.0, ge=0.1, le=5.0)


class UserKeywordResponse(BaseModel):
    """User keyword response"""
    id: int
    keyword: str
    category: Optional[str]
    weight: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


@router.get("/user-keywords", response_model=List[UserKeywordResponse])
async def list_user_keywords(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user personal keywords

    - Returns all keywords for the current user
    - Can filter by category and active status
    """
    from app.models.user_keyword import UserKeyword

    query = db.query(UserKeyword).filter(UserKeyword.user_id == current_user.id)

    if category:
        query = query.filter(UserKeyword.category == category)

    if is_active is not None:
        query = query.filter(UserKeyword.is_active == is_active)

    keywords = query.order_by(UserKeyword.weight.desc()).all()

    return [UserKeywordResponse.model_validate(kw) for kw in keywords]


@router.post("/user-keywords", response_model=UserKeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_user_keyword(
    keyword_data: UserKeywordCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a personal keyword for the current user

    - Creates a new keyword
    - Keyword must be unique per user
    """
    from app.models.user_keyword import UserKeyword

    # Check if keyword already exists for this user
    existing = db.query(UserKeyword).filter(
        UserKeyword.user_id == current_user.id,
        UserKeyword.keyword == keyword_data.keyword
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword already exists"
        )

    # Create new keyword
    keyword = UserKeyword(
        user_id=current_user.id,
        keyword=keyword_data.keyword,
        category=keyword_data.category,
        weight=keyword_data.weight,
        is_active=True,
    )

    db.add(keyword)
    db.commit()
    db.refresh(keyword)

    logger.info(f"User keyword created: user_id={current_user.id}, keyword={keyword.keyword}")

    return UserKeywordResponse.model_validate(keyword)


@router.patch("/user-keywords/{keyword_id}", response_model=UserKeywordResponse)
async def update_user_keyword(
    keyword_id: int,
    keyword_data: UserKeywordCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a personal keyword

    - Can update keyword text, category, and weight
    - Only owner can update
    """
    from app.models.user_keyword import UserKeyword

    keyword = db.query(UserKeyword).filter(
        UserKeyword.id == keyword_id,
        UserKeyword.user_id == current_user.id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    # Check if new keyword text already exists
    if keyword_data.keyword != keyword.keyword:
        existing = db.query(UserKeyword).filter(
            UserKeyword.user_id == current_user.id,
            UserKeyword.keyword == keyword_data.keyword,
            UserKeyword.id != keyword_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keyword already exists"
            )

    keyword.keyword = keyword_data.keyword
    keyword.category = keyword_data.category
    keyword.weight = keyword_data.weight
    keyword.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(keyword)

    logger.info(f"User keyword updated: id={keyword_id}")

    return UserKeywordResponse.model_validate(keyword)


@router.delete("/user-keywords/{keyword_id}", response_model=MessageResponse)
async def delete_user_keyword(
    keyword_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a personal keyword

    - Only owner can delete
    - Hard delete (no soft delete for keywords)
    """
    from app.models.user_keyword import UserKeyword

    keyword = db.query(UserKeyword).filter(
        UserKeyword.id == keyword_id,
        UserKeyword.user_id == current_user.id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    db.delete(keyword)
    db.commit()

    logger.info(f"User keyword deleted: id={keyword_id}")

    return MessageResponse(message="Keyword deleted")
