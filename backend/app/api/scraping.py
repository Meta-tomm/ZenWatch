from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.scraping_run import ScrapingRun
from app.tasks.scraping import scrape_all_sources
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/scraping", tags=["scraping"])


class TriggerScrapingRequest(BaseModel):
    keywords: Optional[List[str]] = None


class TriggerScrapingResponse(BaseModel):
    status: str
    task_id: str
    message: str


class ScrapingStatusResponse(BaseModel):
    task_id: str
    status: str
    source_type: str
    articles_scraped: int
    articles_saved: int
    error_message: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None


class ScrapingStatsResponse(BaseModel):
    total_runs: int
    successful_runs: int
    failed_runs: int
    total_articles_scraped: int
    total_articles_saved: int
    success_rate: float


@router.post("/trigger", response_model=TriggerScrapingResponse, status_code=202)
def trigger_scraping(
    request: TriggerScrapingRequest = TriggerScrapingRequest()
):
    """
    Trigger a new scraping job

    Args:
        request: Optional keywords to filter articles

    Returns:
        Task ID and status
    """
    logger.info(f"Triggering scraping job with keywords: {request.keywords}")

    # Trigger Celery task
    task = scrape_all_sources.delay(keywords=request.keywords)

    return TriggerScrapingResponse(
        status="accepted",
        task_id=task.id,
        message=f"Scraping job started with task ID: {task.id}"
    )


@router.get("/status/{task_id}", response_model=ScrapingStatusResponse)
def get_scraping_status(task_id: str, db: Session = Depends(get_db)):
    """
    Get status of a scraping job

    Args:
        task_id: Celery task ID
        db: Database session

    Returns:
        Scraping run details
    """
    scraping_run = db.query(ScrapingRun).filter_by(task_id=task_id).first()

    if not scraping_run:
        raise HTTPException(
            status_code=404,
            detail=f"Scraping run with task ID {task_id} not found"
        )

    return ScrapingStatusResponse(
        task_id=scraping_run.task_id,
        status=scraping_run.status,
        source_type=scraping_run.source_type,
        articles_scraped=scraping_run.articles_scraped,
        articles_saved=scraping_run.articles_saved,
        error_message=scraping_run.error_message,
        started_at=scraping_run.started_at.isoformat(),
        completed_at=scraping_run.completed_at.isoformat() if scraping_run.completed_at else None
    )


@router.get("/history", response_model=List[ScrapingStatusResponse])
def get_scraping_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent scraping runs

    Args:
        limit: Maximum number of runs to return
        db: Database session

    Returns:
        List of recent scraping runs
    """
    runs = db.query(ScrapingRun).order_by(
        ScrapingRun.started_at.desc()
    ).limit(limit).all()

    return [
        ScrapingStatusResponse(
            task_id=run.task_id,
            status=run.status,
            source_type=run.source_type,
            articles_scraped=run.articles_scraped,
            articles_saved=run.articles_saved,
            error_message=run.error_message,
            started_at=run.started_at.isoformat(),
            completed_at=run.completed_at.isoformat() if run.completed_at else None
        )
        for run in runs
    ]


@router.get("/stats", response_model=ScrapingStatsResponse)
def get_scraping_stats(db: Session = Depends(get_db)):
    """
    Get scraping statistics

    Args:
        db: Database session

    Returns:
        Aggregated statistics
    """
    all_runs = db.query(ScrapingRun).all()

    total_runs = len(all_runs)
    successful_runs = sum(1 for run in all_runs if run.status == 'success')
    failed_runs = sum(1 for run in all_runs if run.status == 'failed')
    total_articles_scraped = sum(run.articles_scraped for run in all_runs)
    total_articles_saved = sum(run.articles_saved for run in all_runs)

    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0.0

    return ScrapingStatsResponse(
        total_runs=total_runs,
        successful_runs=successful_runs,
        failed_runs=failed_runs,
        total_articles_scraped=total_articles_scraped,
        total_articles_saved=total_articles_saved,
        success_rate=round(success_rate, 2)
    )
