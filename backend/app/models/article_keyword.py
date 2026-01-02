from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ArticleKeyword(Base):
    """Table d'association N:N entre Articles et Keywords avec score de pertinence"""

    __tablename__ = "article_keywords"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False)
    relevance_score = Column(Float, default=0.0)  # Score de pertinence pour ce mot-clé
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    article = relationship("Article", back_populates="article_keywords")
    keyword = relationship("Keyword", back_populates="article_keywords")

    # Contrainte unique (article_id, keyword_id)
    __table_args__ = (
        UniqueConstraint("article_id", "keyword_id", name="uq_article_keyword"),
    )

    def __repr__(self):
        return f"<ArticleKeyword(article_id={self.article_id}, keyword_id={self.keyword_id}, score={self.relevance_score})>"
