import pytest
from app.models.source import Source
from app.database import get_db


def test_source_model_creation():
    source = Source(
        name="Reddit",
        type="reddit",
        config={"subreddits": ["programming"]},
        is_active=True
    )
    assert source.name == "Reddit"
    assert source.type == "reddit"
    assert source.is_active == True
