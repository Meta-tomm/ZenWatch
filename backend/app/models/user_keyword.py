"""User keyword model for personalized content scoring"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class UserKeyword(Base):
    """User-specific keywords for content personalization"""

    __tablename__ = "user_keywords"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    keyword = Column(String(100), nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "keyword", name="uq_user_keyword"),
    )

    # Relationships
    user = relationship("User", back_populates="keywords")

    def __repr__(self) -> str:
        return f"<UserKeyword(user_id={self.user_id}, keyword='{self.keyword}', weight={self.weight})>"
