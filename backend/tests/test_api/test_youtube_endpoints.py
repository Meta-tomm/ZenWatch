import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.youtube_channel import YouTubeChannel

client = TestClient(app)

def test_get_youtube_channels_empty(db_session):
    """Test getting channels when none exist"""
    response = client.get("/api/youtube/channels")

    assert response.status_code == 200
    data = response.json()
    assert data['channels'] == []

def test_add_youtube_channel(db_session):
    """Test adding a new channel"""
    channel_data = {
        'channel_id': 'UC_test123',
        'channel_name': 'Test Channel'
    }

    response = client.post("/api/youtube/channels", json=channel_data)

    assert response.status_code == 200
    data = response.json()
    assert data['channel_id'] == 'UC_test123'
    assert data['channel_name'] == 'Test Channel'
    assert data['is_active'] == True

def test_add_duplicate_channel_fails(db_session):
    """Test adding duplicate channel returns error"""
    channel_data = {
        'channel_id': 'UC_test',
        'channel_name': 'Test'
    }

    # Add first time
    client.post("/api/youtube/channels", json=channel_data)

    # Try to add again
    response = client.post("/api/youtube/channels", json=channel_data)

    assert response.status_code == 400
    assert "already exists" in response.json()['detail'].lower()
