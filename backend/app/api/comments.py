"""Comments API routes"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.auth.deps import get_current_user, get_current_user_optional
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Pydantic schemas for comments
class CommentCreate(BaseModel):
    """Create comment request"""
    content: str = Field(..., min_length=1, max_length=5000)
    article_id: Optional[int] = None
    video_id: Optional[int] = None
    parent_id: Optional[int] = None  # For threaded replies


class CommentUpdate(BaseModel):
    """Update comment request"""
    content: str = Field(..., min_length=1, max_length=5000)


class CommentAuthor(BaseModel):
    """Comment author info"""
    id: int
    username: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Comment response"""
    id: int
    content: str
    article_id: Optional[int]
    video_id: Optional[int]
    parent_id: Optional[int]
    author: CommentAuthor
    is_edited: bool
    created_at: datetime
    updated_at: datetime
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


def build_comment_response(comment, include_replies: bool = True) -> CommentResponse:
    """Build comment response with nested replies"""
    author = CommentAuthor(
        id=comment.author.id,
        username=comment.author.username,
        display_name=comment.author.display_name,
        avatar_url=comment.author.avatar_url,
    )

    replies = []
    if include_replies and hasattr(comment, "replies") and comment.replies:
        replies = [build_comment_response(reply, include_replies=True)
                   for reply in comment.replies if not reply.is_deleted]

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        article_id=comment.article_id,
        video_id=comment.video_id,
        parent_id=comment.parent_id,
        author=author,
        is_edited=comment.is_edited,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        replies=replies,
    )


@router.get("/comments/article/{article_id}", response_model=List[CommentResponse])
async def get_article_comments(
    article_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get comments for an article (threaded)

    - Returns top-level comments with nested replies
    - Soft-deleted comments are hidden
    """
    from app.models.comment import Comment
    from app.models.article import Article

    # Verify article exists
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    # Get top-level comments (no parent)
    comments = db.query(Comment).filter(
        Comment.article_id == article_id,
        Comment.parent_id.is_(None),
        Comment.is_deleted == False
    ).order_by(
        Comment.created_at.desc()
    ).limit(limit).offset(offset).all()

    return [build_comment_response(c) for c in comments]


@router.get("/comments/video/{video_id}", response_model=List[CommentResponse])
async def get_video_comments(
    video_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get comments for a video (threaded)

    - Returns top-level comments with nested replies
    - Soft-deleted comments are hidden
    """
    from app.models.comment import Comment
    from app.models.article import Article

    # Verify video exists (videos are articles with is_video=True)
    video = db.query(Article).filter(
        Article.id == video_id,
        Article.is_video == True
    ).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Get top-level comments
    comments = db.query(Comment).filter(
        Comment.video_id == video_id,
        Comment.parent_id.is_(None),
        Comment.is_deleted == False
    ).order_by(
        Comment.created_at.desc()
    ).limit(limit).offset(offset).all()

    return [build_comment_response(c) for c in comments]


@router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new comment

    - Must provide either article_id or video_id
    - parent_id for reply to another comment
    """
    from app.models.comment import Comment
    from app.models.article import Article

    # Validate: must have article_id or video_id
    if not comment_data.article_id and not comment_data.video_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide article_id or video_id"
        )

    if comment_data.article_id and comment_data.video_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot provide both article_id and video_id"
        )

    # Verify article/video exists
    if comment_data.article_id:
        article = db.query(Article).filter(Article.id == comment_data.article_id).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )

    if comment_data.video_id:
        video = db.query(Article).filter(
            Article.id == comment_data.video_id,
            Article.is_video == True
        ).first()
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

    # Verify parent comment exists if replying
    if comment_data.parent_id:
        parent = db.query(Comment).filter(
            Comment.id == comment_data.parent_id,
            Comment.is_deleted == False
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )

    # Create comment
    comment = Comment(
        content=comment_data.content,
        article_id=comment_data.article_id,
        video_id=comment_data.video_id,
        parent_id=comment_data.parent_id,
        user_id=current_user.id,
        is_edited=False,
        is_deleted=False,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    logger.info(f"Comment created: id={comment.id}, user_id={current_user.id}")

    return build_comment_response(comment, include_replies=False)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Edit a comment

    - Only comment author can edit
    - Marks comment as edited
    """
    from app.models.comment import Comment

    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Only author can edit
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit another user comment"
        )

    comment.content = comment_data.content
    comment.is_edited = True
    comment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(comment)

    logger.info(f"Comment updated: id={comment_id}")

    return build_comment_response(comment, include_replies=False)


@router.delete("/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    comment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a comment (soft delete)

    - Only comment author can delete
    - Content is replaced with placeholder
    """
    from app.models.comment import Comment

    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Only author can delete
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user comment"
        )

    # Soft delete
    comment.is_deleted = True
    comment.content = "[deleted]"
    comment.deleted_at = datetime.utcnow()

    db.commit()

    logger.info(f"Comment soft deleted: id={comment_id}")

    return MessageResponse(message="Comment deleted")
