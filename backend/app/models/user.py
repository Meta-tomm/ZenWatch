import uuid
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User account model for authentication and profile management"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    bio = Column(String(500), nullable=True)
    github_url = Column(Text, nullable=True)
    portfolio_url = Column(Text, nullable=True)
    role = Column(String(20), server_default='user', nullable=False)
    is_active = Column(Boolean, server_default='true', nullable=False)
    is_verified = Column(Boolean, server_default='false', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    article_states = relationship("UserArticleState", back_populates="user", cascade="all, delete-orphan")
    video_states = relationship("UserVideoState", back_populates="user", cascade="all, delete-orphan")
    keywords = relationship("UserKeyword", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user")
    consents = relationship("UserConsent", back_populates="user", cascade="all, delete-orphan")
    export_requests = relationship("DataExportRequest", back_populates="user", cascade="all, delete-orphan")
    config = relationship("UserConfig", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class OAuthAccount(Base):
    """OAuth provider account linked to a user"""

    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(20), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    provider_email = Column(String(255), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="oauth_accounts")

    def __repr__(self):
        return f"<OAuthAccount(provider='{self.provider}', user_id={self.user_id})>"
