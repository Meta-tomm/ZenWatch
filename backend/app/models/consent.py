from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserConsent(Base):
    """User consent records for GDPR compliance."""
    __tablename__ = "user_consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    consent_type = Column(String(50), nullable=False)  # 'marketing', 'analytics', 'newsletter', etc.
    given = Column(Boolean, default=False, nullable=False)
    given_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="consents")

    def __repr__(self):
        return f"<UserConsent(user_id={self.user_id}, type='{self.consent_type}', given={self.given})>"


class DataExportRequest(Base):
    """Track user data export requests for GDPR compliance."""
    __tablename__ = "data_export_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, processing, completed, failed
    requested_at = Column(DateTime, server_default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    download_url = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<DataExportRequest(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
