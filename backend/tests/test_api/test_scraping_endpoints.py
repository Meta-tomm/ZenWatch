import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app
from app.models.scraping_run import ScrapingRun
from app.database import get_db
from datetime import datetime


@pytest.fixture
def test_client(db_session):
    """Create test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_trigger_scraping_endpoint(test_client, db_session):
    """Test POST /api/scraping/trigger endpoint"""

    # Mock the Celery task
    with patch('app.api.scraping.scrape_all_sources') as mock_task:
        mock_result = Mock()
        mock_result.id = 'test-task-123'
        mock_task.delay.return_value = mock_result

        response = test_client.post(
            "/api/scraping/trigger",
            json={"keywords": ["python", "AI"]}
        )

        assert response.status_code == 202
        data = response.json()
        assert data['status'] == 'accepted'
        assert data['task_id'] == 'test-task-123'
        assert 'message' in data

        # Verify task was called with keywords
        mock_task.delay.assert_called_once_with(keywords=["python", "AI"])


def test_trigger_scraping_without_keywords(test_client, db_session):
    """Test triggering scraping without specifying keywords (uses defaults)"""

    with patch('app.api.scraping.scrape_all_sources') as mock_task:
        mock_result = Mock()
        mock_result.id = 'test-task-456'
        mock_task.delay.return_value = mock_result

        response = test_client.post("/api/scraping/trigger")

        assert response.status_code == 202
        data = response.json()
        assert data['task_id'] == 'test-task-456'

        # Should be called with None for keywords (defaults in task)
        mock_task.delay.assert_called_once_with(keywords=None)


def test_get_scraping_status(test_client, db_session):
    """Test GET /api/scraping/status/{task_id} endpoint"""

    # Create a scraping run in the database
    scraping_run = ScrapingRun(
        task_id='test-task-789',
        source_type='all',
        status='success',
        articles_scraped=42,
        articles_saved=40,
        completed_at=datetime(2024, 1, 1, 12, 0, 0)
    )
    db_session.add(scraping_run)
    db_session.commit()

    response = test_client.get("/api/scraping/status/test-task-789")

    assert response.status_code == 200
    data = response.json()
    assert data['task_id'] == 'test-task-789'
    assert data['status'] == 'success'
    assert data['articles_scraped'] == 42
    assert data['articles_saved'] == 40
    assert data['source_type'] == 'all'


def test_get_scraping_status_not_found(test_client, db_session):
    """Test getting status for non-existent task"""

    response = test_client.get("/api/scraping/status/nonexistent-task")

    assert response.status_code == 404
    data = response.json()
    assert 'detail' in data


def test_get_recent_scraping_runs(test_client, db_session):
    """Test GET /api/scraping/history endpoint"""

    # Create multiple scraping runs
    for i in range(5):
        run = ScrapingRun(
            task_id=f'task-{i}',
            source_type='all',
            status='success' if i % 2 == 0 else 'failed',
            articles_scraped=i * 10,
            articles_saved=i * 9
        )
        db_session.add(run)
    db_session.commit()

    response = test_client.get("/api/scraping/history?limit=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Verify we got task IDs in the response
    task_ids = [item['task_id'] for item in data]
    assert all(task_id.startswith('task-') for task_id in task_ids)


def test_get_scraping_stats(test_client, db_session):
    """Test GET /api/scraping/stats endpoint"""

    # Create scraping runs with various statuses
    runs_data = [
        {'status': 'success', 'articles_scraped': 100, 'articles_saved': 95},
        {'status': 'success', 'articles_scraped': 50, 'articles_saved': 48},
        {'status': 'failed', 'articles_scraped': 0, 'articles_saved': 0},
        {'status': 'partial_success', 'articles_scraped': 30, 'articles_saved': 25},
    ]

    for i, run_data in enumerate(runs_data):
        run = ScrapingRun(
            task_id=f'stats-task-{i}',
            source_type='all',
            **run_data
        )
        db_session.add(run)
    db_session.commit()

    response = test_client.get("/api/scraping/stats")

    assert response.status_code == 200
    data = response.json()

    assert data['total_runs'] == 4
    assert data['successful_runs'] == 2
    assert data['failed_runs'] == 1
    assert data['total_articles_scraped'] == 180
    assert data['total_articles_saved'] == 168
    assert 'success_rate' in data
