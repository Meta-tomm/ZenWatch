import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.scraped_article import ScrapedYouTubeVideo

def test_scraped_youtube_video_creation():
    """Test creating a YouTube video schema"""
    video = ScrapedYouTubeVideo(
        title='Test Video',
        url='https://youtube.com/watch?v=test123',
        source_type='youtube_rss',
        external_id='test123',
        author='Test Channel',
        published_at=datetime.now(),
        video_id='test123',
        channel_id='UC_test',
        channel_name='Test Channel',
        thumbnail_url='https://i.ytimg.com/vi/test123/hqdefault.jpg',
        duration_seconds=600,
        view_count=1000
    )

    assert video.video_id == 'test123'
    assert video.channel_id == 'UC_test'
    assert video.duration_seconds == 600
    assert video.view_count == 1000

def test_scraped_youtube_video_validation():
    """Test video ID is required"""
    with pytest.raises(ValidationError):
        ScrapedYouTubeVideo(
            title='Test',
            url='https://youtube.com/watch?v=test',
            source_type='youtube_rss',
            external_id='test',
            author='Test',
            published_at=datetime.now()
            # Missing video_id
        )

def test_scraped_youtube_video_empty_channel_name():
    """Test channel_name cannot be empty"""
    with pytest.raises(ValueError):
        ScrapedYouTubeVideo(
            title='Test',
            url='https://youtube.com/watch?v=test',
            source_type='youtube_rss',
            external_id='test',
            author='Test',
            published_at=datetime.now(),
            video_id='test123',
            channel_id='UC_test',
            channel_name='   '  # Whitespace only
        )
