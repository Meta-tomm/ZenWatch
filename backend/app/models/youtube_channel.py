from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from app.database import Base


class YouTubeChannel(Base):
    __tablename__ = "youtube_channels"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(255), nullable=False, unique=True)
    channel_name = Column(String(255), nullable=False)
    channel_url = Column(Text, nullable=False)
    rss_feed_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    subscriber_count = Column(Integer, default=0, server_default='0')
    is_active = Column(Boolean, default=True, server_default='true')
    is_suggested = Column(Boolean, default=False, server_default='false')
    suggestion_score = Column(Float, nullable=True)
    suggestion_reason = Column(Text, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __init__(self, **kwargs):
        # Set defaults explicitly for Python-level instantiation
        kwargs.setdefault('subscriber_count', 0)
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_suggested', False)
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<YouTubeChannel(id={self.id}, name='{self.channel_name}', active={self.is_active})>"
