from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, unique=True)
    base_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    scrape_frequency_hours = Column(Integer, default=6)
    last_scraped_at = Column(DateTime, nullable=True)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
