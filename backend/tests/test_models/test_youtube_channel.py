import pytest
from datetime import datetime
from app.models.youtube_channel import YouTubeChannel

def test_youtube_channel_creation():
    """Test creating a YouTube channel"""
    channel = YouTubeChannel(
        channel_id='UC_test123',
        channel_name='Test Channel',
        channel_url='https://youtube.com/channel/UC_test123',
        rss_feed_url='https://youtube.com/feeds/videos.xml?channel_id=UC_test123',
        is_active=True,
        is_suggested=False
    )

    assert channel.channel_id == 'UC_test123'
    assert channel.channel_name == 'Test Channel'
    assert channel.is_active == True
    assert channel.is_suggested == False

def test_youtube_channel_defaults():
    """Test default values"""
    channel = YouTubeChannel(
        channel_id='UC_test',
        channel_name='Test',
        channel_url='https://example.com',
        rss_feed_url='https://example.com/rss'
    )

    assert channel.subscriber_count == 0
    assert channel.is_active == True
    assert channel.is_suggested == False
    assert channel.suggestion_score is None
