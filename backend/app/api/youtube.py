from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.models.youtube_channel import YouTubeChannel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/youtube/channels")
async def get_youtube_channels(
    include_suggestions: bool = True,
    db: Session = Depends(get_db)
):
    """Get all YouTube channels (subscribed + suggestions)"""
    query = db.query(YouTubeChannel)

    if not include_suggestions:
        query = query.filter(YouTubeChannel.is_active == True)

    channels = query.order_by(
        YouTubeChannel.is_active.desc(),
        YouTubeChannel.suggestion_score.desc()
    ).all()

    return {"channels": channels}


@router.post("/youtube/channels")
async def add_youtube_channel(
    channel_data: Dict,
    db: Session = Depends(get_db)
):
    """Manually add a YouTube channel"""
    channel_id = channel_data.get('channel_id')
    channel_name = channel_data.get('channel_name')

    if not channel_id or not channel_name:
        raise HTTPException(400, "channel_id and channel_name are required")

    # Check if already exists
    existing = db.query(YouTubeChannel).filter_by(channel_id=channel_id).first()
    if existing:
        raise HTTPException(400, "Channel already exists")

    # Create channel
    channel = YouTubeChannel(
        channel_id=channel_id,
        channel_name=channel_name,
        channel_url=f"https://www.youtube.com/channel/{channel_id}",
        rss_feed_url=f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
        is_active=True,
        is_suggested=False
    )

    db.add(channel)
    db.commit()
    db.refresh(channel)

    logger.info(f"Added YouTube channel: {channel_name}")
    return channel


@router.post("/youtube/channels/{channel_id}/accept")
async def accept_suggested_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """Accept an AI-suggested channel"""
    channel = db.query(YouTubeChannel).filter_by(id=channel_id).first()

    if not channel:
        raise HTTPException(404, "Channel not found")

    channel.is_active = True
    db.commit()

    return {"message": "Channel accepted"}


@router.delete("/youtube/channels/{channel_id}")
async def remove_youtube_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """Remove or dismiss a channel"""
    channel = db.query(YouTubeChannel).filter_by(id=channel_id).first()

    if not channel:
        raise HTTPException(404, "Channel not found")

    db.delete(channel)
    db.commit()

    return {"message": "Channel removed"}
