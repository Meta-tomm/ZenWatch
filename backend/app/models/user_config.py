from sqlalchemy import Column, Integer, String, Boolean, Float, Time, DateTime, ARRAY, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from app.database import Base


class UserConfig(Base):
    """Modèle pour la configuration utilisateur"""

    __tablename__ = "user_config"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    daily_digest_enabled = Column(Boolean, default=True, nullable=False)
    digest_time = Column(Time, nullable=False, server_default="08:00:00")  # 08:00 par défaut
    min_score_threshold = Column(Float, default=50.0, nullable=False)  # Score minimum pour les articles
    preferred_categories = Column(PG_ARRAY(Text), nullable=True)  # Array PostgreSQL
    email_frequency = Column(String(20), default="daily", nullable=False)  # daily, weekly
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserConfig(email='{self.email}', digest_enabled={self.daily_digest_enabled})>"
