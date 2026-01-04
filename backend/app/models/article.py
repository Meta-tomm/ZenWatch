import json
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, TypeDecorator, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class JSONEncodedArray(TypeDecorator):
    """
    Stores arrays as JSON in SQLite, uses native ARRAY in PostgreSQL
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(String))
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is None:
            return None
        return json.loads(value)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=True)
    external_id = Column(String(255), nullable=True)
    title = Column(Text, nullable=False)
    url = Column(Text, unique=True, nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=False)
    scraped_at = Column(DateTime, server_default=func.now())
    score = Column(Float, nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(JSONEncodedArray, nullable=True)
    language = Column(String(10), default='en')
    read_time_minutes = Column(Integer, nullable=True)
    upvotes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    is_read = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    video_id = Column(String(255), nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    view_count = Column(Integer, nullable=True)
    is_video = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    source = relationship("Source", back_populates="articles")
    article_keywords = relationship(
        "ArticleKeyword",
        back_populates="article",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', score={self.score})>"
