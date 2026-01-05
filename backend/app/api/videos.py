from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, desc
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Article, Source
from app.schemas.article import VideoResponse, PaginatedVideosResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# YouTube source types
YOUTUBE_SOURCE_TYPES = ['youtube_rss', 'youtube_trending']


@router.get("/videos", response_model=PaginatedVideosResponse)
async def get_videos(
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    sources: Optional[str] = Query(None, description="Comma-separated source types"),
    search: Optional[str] = Query(None, description="Search in title, author"),
    sort: str = Query("score", pattern="^(score|date|popularity)$"),
    timeRange: Optional[str] = Query(None, pattern="^(24h|7d|30d)$", description="Time filter"),
    minScore: float = Query(0.0, ge=0.0, le=100.0),
    is_favorite: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get videos (articles from YouTube sources)

    - **categories**: Filter by categories (comma-separated)
    - **sources**: Filter by YouTube source types (youtube_rss, youtube_trending)
    - **search**: Search in title, author
    - **sort**: Sort by (score, date, popularity)
    - **minScore**: Minimum score (0-100)
    - **is_favorite**: Filter by favorites
    - **limit**: Max results (1-200)
    - **offset**: Offset for pagination
    """
    query = db.query(Article).options(joinedload(Article.source)).join(
        Article.source
    ).filter(
        Source.type.in_(YOUTUBE_SOURCE_TYPES),
        Article.is_archived == False,
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

    # Filter by categories
    if categories:
        category_list = [c.strip() for c in categories.split(',') if c.strip()]
        if category_list:
            query = query.filter(Article.category.in_(category_list))

    # Filter by specific YouTube sources
    if sources:
        source_list = [s.strip() for s in sources.split(',') if s.strip()]
        youtube_sources = [s for s in source_list if s in YOUTUBE_SOURCE_TYPES]
        if youtube_sources:
            query = query.filter(Source.type.in_(youtube_sources))

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.author.ilike(search_term)
            )
        )

    # Filter by favorite
    if is_favorite is not None:
        query = query.filter(Article.is_favorite == is_favorite)

    # Get total count
    total = query.count()

    # Sorting
    if sort == "score":
        query = query.order_by(Article.score.desc())
    elif sort == "date":
        query = query.order_by(Article.published_at.desc())
    elif sort == "popularity":
        query = query.order_by(Article.view_count.desc().nullslast())

    videos = query.limit(limit).offset(offset).all()

    # Build response
    videos_data = []
    for video in videos:
        video_dict = {
            'id': video.id,
            'title': video.title,
            'url': video.url,
            'video_id': video.video_id,
            'thumbnail_url': video.thumbnail_url,
            'duration_seconds': video.duration_seconds,
            'view_count': video.view_count,
            'author': video.author,
            'published_at': video.published_at,
            'score': video.score,
            'category': video.category,
            'summary': video.summary,
            'tags': video.tags or [],
            'is_read': video.is_read,
            'is_favorite': video.is_favorite,
            'is_liked': video.is_liked if hasattr(video, 'is_liked') else False,
            'is_disliked': video.is_disliked if hasattr(video, 'is_disliked') else False,
            'source_type': video.source.type if video.source else None,
            'created_at': video.created_at,
            'updated_at': video.updated_at
        }
        videos_data.append(VideoResponse.model_validate(video_dict))

    logger.info(f"Retrieved {len(videos)} videos (filters: categories={categories}, sources={sources})")

    return PaginatedVideosResponse(
        data=videos_data,
        total=total,
        hasMore=offset + len(videos) < total,
        offset=offset,
        limit=limit
    )


@router.get("/videos/best-of-week", response_model=Optional[VideoResponse])
async def get_best_video_of_week(db: Session = Depends(get_db)):
    """
    Get the best video of the week based on score AND user engagement.

    Ranking formula: score + (is_liked * 15) - (is_disliked * 20)
    - Liked videos get +15 bonus
    - Disliked videos get -20 penalty
    """
    from sqlalchemy import case

    one_week_ago = datetime.utcnow() - timedelta(days=7)

    # Calculate engagement-adjusted score
    engagement_score = (
        func.coalesce(Article.score, 0) +
        case((Article.is_liked == True, 15), else_=0) -
        case((Article.is_disliked == True, 20), else_=0)
    )

    video = db.query(Article).options(joinedload(Article.source)).join(
        Article.source
    ).filter(
        Source.type.in_(YOUTUBE_SOURCE_TYPES),
        Article.published_at >= one_week_ago,
        Article.is_archived == False
    ).order_by(
        engagement_score.desc()
    ).first()

    if not video:
        return None

    return VideoResponse.model_validate({
        'id': video.id,
        'title': video.title,
        'url': video.url,
        'video_id': video.video_id,
        'thumbnail_url': video.thumbnail_url,
        'duration_seconds': video.duration_seconds,
        'view_count': video.view_count,
        'author': video.author,
        'published_at': video.published_at,
        'score': video.score,
        'category': video.category,
        'summary': video.summary,
        'tags': video.tags or [],
        'is_read': video.is_read,
        'is_favorite': video.is_favorite,
        'is_liked': video.is_liked if hasattr(video, 'is_liked') else False,
        'is_disliked': video.is_disliked if hasattr(video, 'is_disliked') else False,
        'source_type': video.source.type if video.source else None,
        'created_at': video.created_at,
        'updated_at': video.updated_at
    })


@router.patch("/videos/{video_id}/favorite", response_model=VideoResponse)
async def toggle_video_favorite(
    video_id: int,
    db: Session = Depends(get_db)
):
    """Toggle favorite on a video"""
    video = db.query(Article).options(joinedload(Article.source)).filter(
        Article.id == video_id
    ).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.is_favorite = not video.is_favorite
    db.commit()
    db.refresh(video)

    logger.info(f"Video {video_id} favorite: {video.is_favorite}")

    return VideoResponse.model_validate({
        'id': video.id,
        'title': video.title,
        'url': video.url,
        'video_id': video.video_id,
        'thumbnail_url': video.thumbnail_url,
        'duration_seconds': video.duration_seconds,
        'view_count': video.view_count,
        'author': video.author,
        'published_at': video.published_at,
        'score': video.score,
        'category': video.category,
        'summary': video.summary,
        'tags': video.tags or [],
        'is_read': video.is_read,
        'is_favorite': video.is_favorite,
        'is_liked': video.is_liked if hasattr(video, 'is_liked') else False,
        'is_disliked': video.is_disliked if hasattr(video, 'is_disliked') else False,
        'source_type': video.source.type if video.source else None,
        'created_at': video.created_at,
        'updated_at': video.updated_at
    })


@router.post("/videos/{video_id}/like", response_model=VideoResponse)
async def toggle_video_like(
    video_id: int,
    db: Session = Depends(get_db)
):
    """Toggle like on a video (removes dislike if set)"""
    video = db.query(Article).options(joinedload(Article.source)).filter(
        Article.id == video_id
    ).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Toggle like, remove dislike if setting like
    if video.is_liked:
        video.is_liked = False
    else:
        video.is_liked = True
        video.is_disliked = False

    db.commit()
    db.refresh(video)

    logger.info(f"Video {video_id} liked: {video.is_liked}")

    return VideoResponse.model_validate({
        'id': video.id,
        'title': video.title,
        'url': video.url,
        'video_id': video.video_id,
        'thumbnail_url': video.thumbnail_url,
        'duration_seconds': video.duration_seconds,
        'view_count': video.view_count,
        'author': video.author,
        'published_at': video.published_at,
        'score': video.score,
        'category': video.category,
        'summary': video.summary,
        'tags': video.tags or [],
        'is_read': video.is_read,
        'is_favorite': video.is_favorite,
        'is_liked': video.is_liked,
        'is_disliked': video.is_disliked,
        'source_type': video.source.type if video.source else None,
        'created_at': video.created_at,
        'updated_at': video.updated_at
    })


@router.post("/videos/{video_id}/dislike", response_model=VideoResponse)
async def toggle_video_dislike(
    video_id: int,
    db: Session = Depends(get_db)
):
    """Toggle dislike on a video (removes like if set)"""
    video = db.query(Article).options(joinedload(Article.source)).filter(
        Article.id == video_id
    ).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Toggle dislike, remove like if setting dislike
    if video.is_disliked:
        video.is_disliked = False
    else:
        video.is_disliked = True
        video.is_liked = False

    db.commit()
    db.refresh(video)

    logger.info(f"Video {video_id} disliked: {video.is_disliked}")

    return VideoResponse.model_validate({
        'id': video.id,
        'title': video.title,
        'url': video.url,
        'video_id': video.video_id,
        'thumbnail_url': video.thumbnail_url,
        'duration_seconds': video.duration_seconds,
        'view_count': video.view_count,
        'author': video.author,
        'published_at': video.published_at,
        'score': video.score,
        'category': video.category,
        'summary': video.summary,
        'tags': video.tags or [],
        'is_read': video.is_read,
        'is_favorite': video.is_favorite,
        'is_liked': video.is_liked,
        'is_disliked': video.is_disliked,
        'source_type': video.source.type if video.source else None,
        'created_at': video.created_at,
        'updated_at': video.updated_at
    })
