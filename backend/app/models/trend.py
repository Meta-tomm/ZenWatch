from sqlalchemy import Column, Integer, String, Float, Date, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class Trend(Base):
    """Modèle pour les tendances détectées"""

    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    trend_score = Column(Float, default=0.0)  # Score de tendance
    article_count = Column(Integer, default=0)  # Nombre d'articles pour ce keyword
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Contrainte unique (keyword, date)
    __table_args__ = (
        UniqueConstraint("keyword", "date", name="uq_keyword_date"),
    )

    def __repr__(self):
        return f"<Trend(keyword='{self.keyword}', score={self.trend_score}, date={self.date})>"
