"""Admin API routes"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.auth.deps import require_admin
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Pydantic schemas for admin
class AdminUserResponse(BaseModel):
    """Admin user response with all fields"""
    id: int
    email: str
    username: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    role: str
    is_active: bool
    email_verified: bool = False
    created_at: datetime
    last_login_at: Optional[datetime]
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    """Admin user update request"""
    role: Optional[str] = Field(None, pattern="^(user|moderator|admin)$")
    is_active: Optional[bool] = None


class PaginatedUsersResponse(BaseModel):
    """Paginated users response"""
    data: List[AdminUserResponse]
    total: int
    hasMore: bool
    offset: int
    limit: int


class AdminCommentResponse(BaseModel):
    """Admin comment response"""
    id: int
    content: str
    article_id: Optional[int]
    video_id: Optional[int]
    user_id: int
    user_email: str
    user_username: Optional[str]
    is_edited: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class PaginatedCommentsResponse(BaseModel):
    """Paginated comments response"""
    data: List[AdminCommentResponse]
    total: int
    hasMore: bool
    offset: int
    limit: int


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


@router.get("/admin/users", response_model=PaginatedUsersResponse)
async def list_users(
    search: Optional[str] = Query(None, description="Search in email, username"),
    role: Optional[str] = Query(None, pattern="^(user|moderator|admin)$"),
    is_active: Optional[bool] = None,
    include_deleted: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only)

    - Paginated with filters
    - Can search by email or username
    - Can filter by role and active status
    """
    from sqlalchemy import or_
    from app.models.user import User

    query = db.query(User)

    # Exclude deleted unless requested
    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.username.ilike(search_term),
                User.display_name.ilike(search_term)
            )
        )

    # Filter by role
    if role:
        query = query.filter(User.role == role)

    # Filter by active status
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Get total count
    total = query.count()

    # Order and paginate
    users = query.order_by(User.created_at.desc()).limit(limit).offset(offset).all()

    return PaginatedUsersResponse(
        data=[AdminUserResponse.model_validate(u) for u in users],
        total=total,
        hasMore=offset + len(users) < total,
        offset=offset,
        limit=limit,
    )


@router.patch("/admin/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: int,
    update_data: AdminUserUpdate,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user role or active status (admin only)

    - Can change role to user, moderator, or admin
    - Can enable/disable accounts
    """
    from app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from demoting themselves
    if user.id == admin.id and update_data.role and update_data.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself"
        )

    # Prevent admin from disabling themselves
    if user.id == admin.id and update_data.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account"
        )

    # Update fields
    if update_data.role is not None:
        user.role = update_data.role
    if update_data.is_active is not None:
        user.is_active = update_data.is_active

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    logger.info(f"Admin updated user: id={user_id}, by={admin.id}")

    return AdminUserResponse.model_validate(user)


@router.delete("/admin/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    hard_delete: bool = False,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete user (admin only)

    - Default: soft delete (anonymize data)
    - hard_delete=true: permanently remove (irreversible)
    """
    from app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deleting yourself
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    if hard_delete:
        # Hard delete - remove from database
        db.delete(user)
        db.commit()
        logger.info(f"Admin hard deleted user: id={user_id}, by={admin.id}")
        return MessageResponse(message="User permanently deleted")
    else:
        # Soft delete - anonymize data
        user.is_active = False
        user.email = f"deleted_{user.id}@deleted.local"
        user.username = f"deleted_{user.id}"
        user.display_name = "Deleted User"
        user.password_hash = None
        user.avatar_url = None
        user.bio = None
        user.deleted_at = datetime.utcnow()
        db.commit()
        logger.info(f"Admin soft deleted user: id={user_id}, by={admin.id}")
        return MessageResponse(message="User account deleted")


@router.get("/admin/comments", response_model=PaginatedCommentsResponse)
async def list_comments(
    search: Optional[str] = Query(None, description="Search in content"),
    user_id: Optional[int] = None,
    article_id: Optional[int] = None,
    video_id: Optional[int] = None,
    is_deleted: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all comments for moderation (admin only)

    - Paginated with filters
    - Can filter by user, article, video
    - Can filter by deleted status
    """
    from app.models.comment import Comment
    from app.models.user import User

    query = db.query(Comment).join(User)

    # Search in content
    if search:
        query = query.filter(Comment.content.ilike(f"%{search}%"))

    # Filter by user
    if user_id:
        query = query.filter(Comment.user_id == user_id)

    # Filter by article
    if article_id:
        query = query.filter(Comment.article_id == article_id)

    # Filter by video
    if video_id:
        query = query.filter(Comment.video_id == video_id)

    # Filter by deleted status
    if is_deleted is not None:
        query = query.filter(Comment.is_deleted == is_deleted)

    # Get total count
    total = query.count()

    # Order and paginate
    comments = query.order_by(Comment.created_at.desc()).limit(limit).offset(offset).all()

    comment_responses = []
    for c in comments:
        comment_responses.append(AdminCommentResponse(
            id=c.id,
            content=c.content,
            article_id=c.article_id,
            video_id=c.video_id,
            user_id=c.user_id,
            user_email=c.author.email,
            user_username=c.author.username,
            is_edited=c.is_edited,
            is_deleted=c.is_deleted,
            created_at=c.created_at,
            updated_at=c.updated_at,
        ))

    return PaginatedCommentsResponse(
        data=comment_responses,
        total=total,
        hasMore=offset + len(comments) < total,
        offset=offset,
        limit=limit,
    )


@router.delete("/admin/comments/{comment_id}", response_model=MessageResponse)
async def hard_delete_comment(
    comment_id: int,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Hard delete a comment (admin only)

    - Permanently removes comment from database
    - Irreversible action
    """
    from app.models.comment import Comment

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    db.delete(comment)
    db.commit()

    logger.info(f"Admin hard deleted comment: id={comment_id}, by={admin.id}")

    return MessageResponse(message="Comment permanently deleted")
