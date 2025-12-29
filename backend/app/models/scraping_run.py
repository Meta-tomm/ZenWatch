from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class ScrapingRun(Base):
    __tablename__ = "scraping_runs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True)
    source_type = Column(String(50), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)
    articles_scraped = Column(Integer, default=0)
    articles_saved = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
