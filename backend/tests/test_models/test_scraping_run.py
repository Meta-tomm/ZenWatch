from app.models.scraping_run import ScrapingRun


def test_scraping_run_model():
    run = ScrapingRun(
        task_id="test-123",
        source_type="reddit",
        status="success",
        articles_scraped=50
    )
    assert run.task_id == "test-123"
    assert run.status == "success"
