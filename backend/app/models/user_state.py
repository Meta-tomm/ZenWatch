"""User state models for tracking article and video interactions"""

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class UserArticleState(Base):
    """Tracks user interaction state with articles"""

    __tablename__ = "user_article_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    is_read = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="uq_user_article_state"),
    )

    # Relationships
    user = relationship("User", back_populates="article_states")
    article = relationship("Article")

    def __repr__(self) -> str:
        return f"<UserArticleState(user_id={self.user_id}, article_id={self.article_id})>"


class UserVideoState(Base):
    """Tracks user interaction state with videos (videos are articles with is_video=True)"""

    __tablename__ = "user_video_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    video_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    is_read = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="uq_user_video_state"),
    )

    # Relationships
    user = relationship("User", back_populates="video_states")
    video = relationship("Article")

    def __repr__(self) -> str:
        return f"<UserVideoState(user_id={self.user_id}, video_id={self.video_id})>"
