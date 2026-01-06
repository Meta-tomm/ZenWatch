"""GDPR consent and data export models"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class UserConsent(Base):
    """GDPR consent tracking for various consent types"""

    __tablename__ = "user_consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    consent_type = Column(String(50), nullable=False)
    consented = Column(Boolean, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    consented_at = Column(DateTime(timezone=True), server_default=func.now())
    withdrawn_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "consent_type IN ('terms', 'privacy', 'marketing', 'analytics')",
            name="check_consent_type",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="consents")

    def __repr__(self) -> str:
        return f"<UserConsent(user_id={self.user_id}, type='{self.consent_type}', consented={self.consented})>"


class DataExportRequest(Base):
    """GDPR data export request tracking"""

    __tablename__ = "data_export_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String(20), default="pending", nullable=False)
    file_url = Column(Text, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed', 'expired')",
            name="check_export_status",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="data_export_requests")

    def __repr__(self) -> str:
        return f"<DataExportRequest(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
