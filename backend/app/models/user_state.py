from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserArticleState(Base):
    """User-specific state for articles (read, favorite, like/dislike)."""
    __tablename__ = "user_article_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_liked = Column(Boolean, default=False, nullable=False)
    is_disliked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Unique constraint: one state per user per article
    __table_args__ = (
        UniqueConstraint('user_id', 'article_id', name='uix_user_article'),
    )

    # Relationships
    user = relationship("User", back_populates="article_states")

    def __repr__(self):
        return f"<UserArticleState(user_id={self.user_id}, article_id={self.article_id})>"


class UserVideoState(Base):
    """User-specific state for videos (read, favorite, like/dislike)."""
    __tablename__ = "user_video_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_liked = Column(Boolean, default=False, nullable=False)
    is_disliked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Unique constraint: one state per user per video
    __table_args__ = (
        UniqueConstraint('user_id', 'video_id', name='uix_user_video'),
    )

    # Relationships
    user = relationship("User", back_populates="video_states")

    def __repr__(self):
        return f"<UserVideoState(user_id={self.user_id}, video_id={self.video_id})>"
