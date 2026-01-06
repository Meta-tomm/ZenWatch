from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database import get_db

# Import models (will be created by models branch)
from app.models.user import User
from app.models.user_keyword import UserKeyword
from app.schemas.user_keyword import (
    UserKeywordCreate,
    UserKeywordList,
    UserKeywordResponse,
    UserKeywordUpdate,
)
from app.services.user_scoring import UserScoringService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/user-keywords", tags=["user-keywords"])


@router.get("", response_model=UserKeywordList)
async def list_user_keywords(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all keywords for the current user.
    """
    keywords = db.query(UserKeyword).filter(
        UserKeyword.user_id == user.id
    ).order_by(UserKeyword.created_at.desc()).all()

    return UserKeywordList(
        data=[UserKeywordResponse.model_validate(k) for k in keywords],
        total=len(keywords)
    )


@router.post("", response_model=UserKeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_user_keyword(
    data: UserKeywordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new keyword for the current user.
    """
    # Check if keyword already exists for this user
    existing = db.query(UserKeyword).filter(
        UserKeyword.user_id == user.id,
        UserKeyword.keyword == data.keyword
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Keyword already exists"
        )

    keyword = UserKeyword(
        user_id=user.id,
        keyword=data.keyword,
        category=data.category,
        weight=data.weight,
        is_active=True,
    )
    db.add(keyword)
    db.commit()
    db.refresh(keyword)

    logger.info(f"User keyword created: {keyword.keyword} for user {user.id}")
    return UserKeywordResponse.model_validate(keyword)


@router.patch("/{keyword_id}", response_model=UserKeywordResponse)
async def update_user_keyword(
    keyword_id: int,
    data: UserKeywordUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing user keyword.
    """
    keyword = db.query(UserKeyword).filter(
        UserKeyword.id == keyword_id,
        UserKeyword.user_id == user.id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(keyword, field, value)

    db.commit()
    db.refresh(keyword)

    logger.info(f"User keyword updated: {keyword.keyword} for user {user.id}")
    return UserKeywordResponse.model_validate(keyword)


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_keyword(
    keyword_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user keyword.
    """
    keyword = db.query(UserKeyword).filter(
        UserKeyword.id == keyword_id,
        UserKeyword.user_id == user.id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    db.delete(keyword)
    db.commit()

    logger.info(f"User keyword deleted: {keyword.keyword} for user {user.id}")
    return None


@router.post("/rescore", status_code=status.HTTP_202_ACCEPTED)
async def rescore_articles(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger rescoring of all articles for the current user.
    Called after keyword changes to recalculate personalized scores.
    Runs in background to avoid blocking.
    """
    def do_rescore():
        scoring_service = UserScoringService(db)
        count = scoring_service.rescore_user_articles(user.id)
        logger.info(f"Rescored {count} articles for user {user.id}")

    background_tasks.add_task(do_rescore)

    logger.info(f"Rescoring triggered for user {user.id}")
    return {"message": "Rescoring started", "status": "processing"}
