from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database import get_db
from app.models.comment import Comment
from app.models.consent import DataExportRequest, UserConsent

# Import models (will be created by models branch)
from app.models.user import User
from app.models.user_keyword import UserKeyword
from app.models.user_state import UserArticleState, UserVideoState
from app.schemas.comment import CommentResponse
from app.schemas.user import (
    UserExportData,
    UserPublicProfile,
    UserResponse,
    UserUpdate,
)
from app.schemas.user_keyword import UserKeywordResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user: User = Depends(get_current_user)
):
    """
    Get the current authenticated user's profile.
    """
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    updates: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile.

    Only provided fields will be updated.
    """
    # Check username uniqueness if changing
    if updates.username and updates.username != user.username:
        existing = db.query(User).filter(
            User.username == updates.username,
            User.id != user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )

    # Update fields
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    logger.info(f"User profile updated: {user.email}")
    return UserResponse.model_validate(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's account.

    This is a soft delete - the account is deactivated but data is preserved
    for a period to allow recovery.
    """
    user.is_active = False
    user.deleted_at = datetime.now(UTC)

    db.commit()

    logger.info(f"User account deleted: {user.email}")
    return None


@router.get("/me/export")
async def export_user_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data (GDPR compliance).

    Returns a JSON file with all user-related data.
    """
    # Collect user keywords
    keywords = db.query(UserKeyword).filter(UserKeyword.user_id == user.id).all()

    # Collect comments
    comments = db.query(Comment).filter(
        Comment.author_id == user.id,
        Comment.is_deleted.is_(False)
    ).all()

    # Collect article states
    article_states = db.query(UserArticleState).filter(
        UserArticleState.user_id == user.id
    ).all()

    # Collect video states
    video_states = db.query(UserVideoState).filter(
        UserVideoState.user_id == user.id
    ).all()

    # Collect consents
    consents = db.query(UserConsent).filter(
        UserConsent.user_id == user.id
    ).all()

    # Record the export request
    export_request = DataExportRequest(
        user_id=user.id,
        status="completed",
        completed_at=datetime.now(UTC),
    )
    db.add(export_request)
    db.commit()

    export_data = UserExportData(
        user=UserResponse.model_validate(user),
        keywords=[UserKeywordResponse.model_validate(k) for k in keywords],
        comments=[CommentResponse.model_validate(c) for c in comments],
        article_states=[
            {
                "article_id": s.article_id,
                "is_read": s.is_read,
                "is_favorite": s.is_favorite,
                "is_liked": s.is_liked,
                "is_disliked": s.is_disliked,
            }
            for s in article_states
        ],
        video_states=[
            {
                "video_id": s.video_id,
                "is_read": s.is_read,
                "is_favorite": s.is_favorite,
                "is_liked": s.is_liked,
                "is_disliked": s.is_disliked,
            }
            for s in video_states
        ],
        consents=[
            {
                "consent_type": c.consent_type,
                "given": c.given,
                "given_at": c.given_at.isoformat() if c.given_at else None,
            }
            for c in consents
        ],
        export_date=datetime.now(UTC),
    )

    logger.info(f"User data exported: {user.email}")

    return JSONResponse(
        content=export_data.model_dump(mode="json"),
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{user.id}.json"
        }
    )


@router.get("/{username}/profile", response_model=UserPublicProfile)
async def get_public_profile(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Get a user's public profile by username.
    """
    user = db.query(User).filter(
        User.username == username,
        User.is_active.is_(True)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserPublicProfile.model_validate(user)
