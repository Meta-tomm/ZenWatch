from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.auth.deps import require_admin
from app.database import get_db
from app.models.comment import Comment

# Import models (will be created by models branch)
from app.models.user import User
from app.schemas.comment import (
    AdminCommentResponse,
    CommentAuthor,
    PaginatedCommentsResponse,
)
from app.schemas.user import (
    AdminUserUpdate,
    PaginatedUsersResponse,
    UserResponse,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=PaginatedUsersResponse)
async def list_users(
    search: Optional[str] = Query(None, description="Search in email or username"),
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only).

    Supports filtering by active status and search.
    """
    query = db.query(User)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_term)) | (User.username.ilike(search_term))
        )

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)

    total = query.count()

    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    return PaginatedUsersResponse(
        data=[UserResponse.model_validate(u) for u in users],
        total=total,
        hasMore=offset + len(users) < total,
        offset=offset,
        limit=limit,
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    updates: AdminUserUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user (admin only).

    Can modify is_active, is_admin, email, username.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent removing own admin status
    if user.id == admin.id and updates.is_admin is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own admin status"
        )

    # Check email uniqueness if changing
    if updates.email and updates.email != user.email:
        existing = db.query(User).filter(
            User.email == updates.email,
            User.id != user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )

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

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    logger.info(f"Admin {admin.id} updated user {user.id}: {update_data}")
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only).

    This permanently deletes the user account.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deletion
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account via admin endpoint"
        )

    db.delete(user)
    db.commit()

    logger.info(f"Admin {admin.id} deleted user {user_id}")
    return None


@router.get("/comments", response_model=PaginatedCommentsResponse)
async def list_comments(
    search: Optional[str] = Query(None, description="Search in content"),
    is_deleted: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all comments (admin only).

    Includes deleted comments.
    """
    query = db.query(Comment).options(joinedload(Comment.author))

    if search:
        query = query.filter(Comment.content.ilike(f"%{search}%"))

    if is_deleted is not None:
        query = query.filter(Comment.is_deleted == is_deleted)

    total = query.count()

    comments = query.order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()

    data = [
        AdminCommentResponse(
            id=c.id,
            content=c.content,
            target_type=c.target_type,
            target_id=c.target_id,
            parent_id=c.parent_id,
            author=CommentAuthor(
                id=c.author.id,
                username=c.author.username,
                display_name=c.author.display_name,
                avatar_url=c.author.avatar_url,
            ),
            is_edited=c.is_edited,
            is_deleted=c.is_deleted,
            created_at=c.created_at,
            updated_at=c.updated_at,
            author_email=c.author.email,
        )
        for c in comments
    ]

    return PaginatedCommentsResponse(
        data=data,
        total=total,
        hasMore=offset + len(comments) < total,
        offset=offset,
        limit=limit,
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_comment(
    comment_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Permanently delete a comment (admin only).

    This is a hard delete - the comment is removed from the database.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    db.delete(comment)
    db.commit()

    logger.info(f"Admin {admin.id} hard deleted comment {comment_id}")
    return None
