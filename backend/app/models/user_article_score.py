from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserArticleScore(Base):
    """
    Per-user personalized scores for articles.

    Each user gets their own score for each article based on their keywords.
    This allows personalized feeds where the same article has different
    relevance scores for different users.
    """
    __tablename__ = "user_article_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False, default=0.0)
    keyword_matches = Column(Integer, default=0)  # Number of keywords matched
    scored_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="article_scores")
    article = relationship("Article", backref="user_scores")

    # Unique constraint: one score per user per article
    __table_args__ = (
        UniqueConstraint('user_id', 'article_id', name='uix_user_article_score'),
    )

    def __repr__(self):
        return f"<UserArticleScore(user_id={self.user_id}, article_id={self.article_id}, score={self.score})>"
