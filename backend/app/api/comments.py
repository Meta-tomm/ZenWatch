from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth.deps import get_current_user
from app.database import get_db
from app.models.comment import Comment

# Import models (will be created by models branch)
from app.models.user import User
from app.schemas.comment import (
    CommentAuthor,
    CommentCreate,
    CommentResponse,
    CommentTargetType,
    CommentUpdate,
    PaginatedCommentsResponse,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/comments", tags=["comments"])


def _build_comment_response(comment: Comment, replies_count: int = 0) -> CommentResponse:
    """Build comment response with author info."""
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        target_type=comment.target_type,
        target_id=comment.target_id,
        parent_id=comment.parent_id,
        author=CommentAuthor(
            id=comment.author.id,
            username=comment.author.username,
            display_name=comment.author.display_name,
            avatar_url=comment.author.avatar_url,
        ),
        is_edited=comment.is_edited,
        is_deleted=comment.is_deleted,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        replies_count=replies_count,
    )


@router.get("/article/{article_id}", response_model=PaginatedCommentsResponse)
async def get_article_comments(
    article_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get comments for an article.

    Returns top-level comments with reply counts.
    """
    # Get top-level comments (no parent)
    query = db.query(Comment).options(joinedload(Comment.author)).filter(
        Comment.target_type == CommentTargetType.ARTICLE,
        Comment.target_id == article_id,
        Comment.parent_id.is_(None),
        Comment.is_deleted.is_(False),
    )

    total = query.count()

    comments = query.order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()

    # Get reply counts for each comment
    reply_counts = {}
    if comments:
        comment_ids = [c.id for c in comments]
        counts = db.query(
            Comment.parent_id,
            func.count(Comment.id)
        ).filter(
            Comment.parent_id.in_(comment_ids),
            Comment.is_deleted.is_(False)
        ).group_by(Comment.parent_id).all()

        reply_counts = {parent_id: count for parent_id, count in counts}

    data = [
        _build_comment_response(c, reply_counts.get(c.id, 0))
        for c in comments
    ]

    return PaginatedCommentsResponse(
        data=data,
        total=total,
        hasMore=offset + len(comments) < total,
        offset=offset,
        limit=limit,
    )


@router.get("/video/{video_id}", response_model=PaginatedCommentsResponse)
async def get_video_comments(
    video_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get comments for a video.

    Returns top-level comments with reply counts.
    """
    query = db.query(Comment).options(joinedload(Comment.author)).filter(
        Comment.target_type == CommentTargetType.VIDEO,
        Comment.target_id == video_id,
        Comment.parent_id.is_(None),
        Comment.is_deleted.is_(False),
    )

    total = query.count()

    comments = query.order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()

    # Get reply counts
    reply_counts = {}
    if comments:
        comment_ids = [c.id for c in comments]
        counts = db.query(
            Comment.parent_id,
            func.count(Comment.id)
        ).filter(
            Comment.parent_id.in_(comment_ids),
            Comment.is_deleted.is_(False)
        ).group_by(Comment.parent_id).all()

        reply_counts = {parent_id: count for parent_id, count in counts}

    data = [
        _build_comment_response(c, reply_counts.get(c.id, 0))
        for c in comments
    ]

    return PaginatedCommentsResponse(
        data=data,
        total=total,
        hasMore=offset + len(comments) < total,
        offset=offset,
        limit=limit,
    )


@router.get("/{comment_id}/replies", response_model=PaginatedCommentsResponse)
async def get_comment_replies(
    comment_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get replies to a specific comment.
    """
    # Verify parent comment exists
    parent = db.query(Comment).filter(Comment.id == comment_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    query = db.query(Comment).options(joinedload(Comment.author)).filter(
        Comment.parent_id == comment_id,
        Comment.is_deleted.is_(False),
    )

    total = query.count()

    replies = query.order_by(Comment.created_at.asc()).offset(offset).limit(limit).all()

    data = [_build_comment_response(r) for r in replies]

    return PaginatedCommentsResponse(
        data=data,
        total=total,
        hasMore=offset + len(replies) < total,
        offset=offset,
        limit=limit,
    )


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new comment.
    """
    # Verify parent comment if replying
    if data.parent_id:
        parent = db.query(Comment).filter(
            Comment.id == data.parent_id,
            Comment.is_deleted.is_(False)
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
        # Ensure reply is on same target
        if parent.target_type != data.target_type or parent.target_id != data.target_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reply must be on same content as parent"
            )

    comment = Comment(
        content=data.content,
        target_type=data.target_type,
        target_id=data.target_id,
        parent_id=data.parent_id,
        author_id=user.id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Reload with author relationship
    comment = db.query(Comment).options(joinedload(Comment.author)).filter(
        Comment.id == comment.id
    ).first()

    logger.info(f"Comment created: {comment.id} by user {user.id}")
    return _build_comment_response(comment)


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    data: CommentUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Edit an existing comment.

    Only the author can edit their own comments.
    """
    comment = db.query(Comment).options(joinedload(Comment.author)).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit other users' comments"
        )

    if comment.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit deleted comment"
        )

    comment.content = data.content
    comment.is_edited = True
    db.commit()
    db.refresh(comment)

    logger.info(f"Comment updated: {comment.id} by user {user.id}")
    return _build_comment_response(comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a comment.

    Only the author can delete their own comments.
    Content is replaced with "[deleted]".
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users' comments"
        )

    comment.is_deleted = True
    comment.content = "[deleted]"
    db.commit()

    logger.info(f"Comment soft deleted: {comment.id} by user {user.id}")
    return None
