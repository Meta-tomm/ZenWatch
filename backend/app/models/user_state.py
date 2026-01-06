from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserArticleState(Base):
    """Per-user state for articles (read status, favorites)"""

    __tablename__ = "user_article_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    is_read = Column(Boolean, server_default='false', nullable=False)
    is_favorite = Column(Boolean, server_default='false', nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="article_states")
    article = relationship("Article")

    def __repr__(self):
        return f"<UserArticleState(user_id={self.user_id}, article_id={self.article_id})>"


class UserVideoState(Base):
    """Per-user state for videos (read status, favorites)"""

    __tablename__ = "user_video_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    is_read = Column(Boolean, server_default='false', nullable=False)
    is_favorite = Column(Boolean, server_default='false', nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="video_states")
    video = relationship("Article")

    def __repr__(self):
        return f"<UserVideoState(user_id={self.user_id}, video_id={self.video_id})>"
