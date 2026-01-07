"""User configuration model for preferences and settings"""

from sqlalchemy import Column, Integer, String, Boolean, Float, Time, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship

from app.database import Base


class UserConfig(Base):
    """User preferences and notification settings"""

    __tablename__ = "user_config"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
        index=True,
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    daily_digest_enabled = Column(Boolean, default=True, nullable=False)
    digest_time = Column(Time, nullable=False, server_default="08:00:00")
    min_score_threshold = Column(Float, default=50.0, nullable=False)
    preferred_categories = Column(PG_ARRAY(Text), nullable=True)
    email_frequency = Column(String(20), default="daily", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="config")

    def __repr__(self) -> str:
        return f"<UserConfig(email='{self.email}', digest_enabled={self.daily_digest_enabled})>"
