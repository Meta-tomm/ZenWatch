from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Keyword(Base):
    """Modèle pour les mots-clés de veille"""

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(200), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    weight = Column(Float, nullable=False, default=1.0)  # 1.0-5.0
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship avec articles via table association
    article_keywords = relationship(
        "ArticleKeyword",
        back_populates="keyword",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Keyword(id={self.id}, keyword='{self.keyword}', weight={self.weight})>"
