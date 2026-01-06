from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Comment(Base):
    """User comments on articles or videos with threaded reply support"""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=True)
    video_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=True)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    is_deleted = Column(Boolean, server_default='false', nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="comments")
    article = relationship("Article", foreign_keys=[article_id])
    video = relationship("Article", foreign_keys=[video_id])
    parent = relationship("Comment", remote_side=[id], backref="replies")

    def __repr__(self):
        target = f"article_id={self.article_id}" if self.article_id else f"video_id={self.video_id}"
        return f"<Comment(id={self.id}, user_id={self.user_id}, {target})>"
