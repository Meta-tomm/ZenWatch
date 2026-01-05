# YouTube Integration Design

**Date**: 2026-01-03
**Status**: Design Complete - Ready for Implementation
**Author**: Design Session with User

## Overview

Add YouTube as a content source for TechWatch, enabling users to track new videos from specific channels and discover trending tech content. Integration includes AI-powered channel suggestions using Gemini API.

## Requirements

### Core Features
1. **New uploads tracking** - Monitor subscribed YouTube channels via RSS feeds
2. **Trending discovery** - Fetch trending videos from tech categories via YouTube Data API
3. **Hybrid channel management** - Manual subscriptions + AI-powered suggestions
4. **Unified feed integration** - Videos displayed alongside articles with special indicators
5. **AI-powered suggestions** - Combined keyword matching + Gemini API quality ranking

### User Experience
- Videos appear in main feed with video badges and thumbnails
- Click to preview embedded video or open on YouTube
- Manage channel subscriptions in Configuration page
- Receive daily AI-suggested channels based on viewing patterns
- Filter feed to show videos only

## Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                     YouTube Integration                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  RSS Scraper     │  │ Trending Scraper │                │
│  │  (Every 30min)   │  │  (Every 6 hours) │                │
│  └────────┬─────────┘  └────────┬─────────┘                │
│           │                     │                            │
│           └──────────┬──────────┘                            │
│                      │                                       │
│           ┌──────────▼──────────┐                           │
│           │   Articles Table    │                           │
│           │ (is_video = true)   │                           │
│           └──────────┬──────────┘                           │
│                      │                                       │
│           ┌──────────▼──────────────┐                       │
│           │  Discovery Engine       │                       │
│           │  (Daily at 2 AM)        │                       │
│           │  - Keyword Analysis     │                       │
│           │  - Gemini AI Ranking    │                       │
│           └─────────────────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User subscribes to channel** → Store in `youtube_channels` table
2. **RSS Scraper (every 30min)** → Fetch new videos → Parse + validate → Save to `articles`
3. **Trending Scraper (every 6h)** → YouTube API → Filter by keywords → Save to `articles`
4. **Discovery Engine (daily)** → Analyze video patterns → Gemini ranks candidates → Suggest channels
5. **Frontend** → Unified feed with video badges + embed preview

### Quota Management

**YouTube Data API v3 Free Tier**: 10,000 units/day

**Strategy**:
- **RSS feeds**: Unlimited, no quota (primary method for uploads)
- **Trending API**: ~100 units/request, 4 requests/day = 400 units
- **Metadata enrichment**: Remaining 9,600 units for on-demand data

**Gemini API Free Tier**: 15 requests/min, 1,500 requests/day
- Daily discovery: ~20-50 channel analyses = well within limits

## Database Schema

### New Tables

#### youtube_channels
```sql
CREATE TABLE youtube_channels (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(255) NOT NULL UNIQUE,  -- YouTube channel ID (UC...)
    channel_name VARCHAR(255) NOT NULL,
    channel_url TEXT NOT NULL,
    rss_feed_url TEXT NOT NULL,
    thumbnail_url TEXT,
    subscriber_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_suggested BOOLEAN DEFAULT FALSE,  -- User-added vs AI-suggested
    suggestion_score FLOAT,  -- AI relevance score (0-100)
    suggestion_reason TEXT,  -- Why suggested (shown in UI)
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_youtube_channels_active ON youtube_channels(is_active);
CREATE INDEX idx_youtube_channels_suggested ON youtube_channels(is_suggested, suggestion_score);
```

#### youtube_channel_stats
```sql
CREATE TABLE youtube_channel_stats (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES youtube_channels(id) ON DELETE CASCADE,
    videos_fetched INTEGER DEFAULT 0,
    avg_score FLOAT,  -- Average relevance score
    match_rate FLOAT,  -- Percentage of videos matching keywords
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(channel_id, date)
);

CREATE INDEX idx_youtube_stats_date ON youtube_channel_stats(date);
```

### Extended articles Table

Add columns:
```sql
ALTER TABLE articles ADD COLUMN video_id VARCHAR(255);
ALTER TABLE articles ADD COLUMN thumbnail_url TEXT;
ALTER TABLE articles ADD COLUMN duration_seconds INTEGER;
ALTER TABLE articles ADD COLUMN view_count INTEGER;
ALTER TABLE articles ADD COLUMN is_video BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_articles_video ON articles(is_video);
CREATE UNIQUE INDEX idx_articles_youtube_video ON articles(source_type, external_id)
    WHERE source_type = 'youtube';
```

## Implementation Details

### 1. YouTube RSS Scraper

**File**: `backend/app/scrapers/plugins/youtube_rss.py`

**Strategy**:
- YouTube RSS feed format: `https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}`
- Parse with `feedparser` library
- No API quota used
- Run every 30 minutes

**Implementation**:
```python
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
import feedparser

@scraper_plugin(name="youtube_rss", display_name="YouTube RSS", version="1.0.0")
class YouTubeRSSScraper(ScraperPlugin):
    """
    YouTube RSS scraper for channel uploads

    Features:
    - Monitors RSS feeds from subscribed channels
    - No API quota consumption
    - Fast and reliable
    - Runs every 30 minutes
    """

    CACHE_TTL = 1800  # 30 minutes

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape new videos from subscribed YouTube channels

        Args:
            config: Scraper configuration (unused, fetches all active channels)
            keywords: Filter videos by keywords (optional)

        Returns:
            List of ScrapedArticle objects with video data
        """
        # Fetch all active channels from database
        channels = await self._get_active_channels()

        videos = []
        for channel in channels:
            try:
                # Fetch RSS feed
                feed = feedparser.parse(channel.rss_feed_url)

                if feed.bozo:
                    self.logger.warning(f"Malformed RSS for {channel.name}")
                    continue

                # Parse entries
                for entry in feed.entries:
                    video = self._parse_rss_entry(entry, channel)

                    # Optional keyword filtering
                    if keywords and not self._matches_keywords(video, keywords):
                        continue

                    videos.append(video)

                # Update last_checked_at
                await self._update_channel_check_time(channel.id)

            except Exception as e:
                self.logger.error(f"RSS error for {channel.name}: {e}")
                continue

        self.logger.info(f"Scraped {len(videos)} videos from {len(channels)} channels")
        return videos

    def _parse_rss_entry(self, entry, channel) -> ScrapedArticle:
        """Parse RSS entry to ScrapedArticle"""
        # Extract video ID from link
        video_id = entry.yt_videoid  # feedparser extracts this

        return ScrapedArticle(
            title=entry.title,
            url=entry.link,
            source_type='youtube_rss',
            external_id=video_id,
            content=entry.get('summary', ''),
            author=channel.channel_name,
            published_at=datetime(*entry.published_parsed[:6]),
            tags=[channel.channel_name],
            # YouTube-specific fields stored in raw_data
            raw_data={
                'video_id': video_id,
                'channel_id': channel.channel_id,
                'thumbnail_url': entry.media_thumbnail[0]['url'] if entry.media_thumbnail else None,
            }
        )
```

### 2. YouTube Trending Scraper

**File**: `backend/app/scrapers/plugins/youtube_trending.py`

**Strategy**:
- YouTube Data API v3 `search.list` endpoint
- Category IDs: Science & Technology (28), Education (27)
- Filter: published in last 7 days, order by viewCount
- Run every 6 hours

**Implementation**:
```python
from googleapiclient.discovery import build
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.config import settings

@scraper_plugin(name="youtube_trending", display_name="YouTube Trending", version="1.0.0")
class YouTubeTrendingScraper(ScraperPlugin):
    """
    YouTube trending videos scraper using Data API v3

    Features:
    - Fetches trending tech videos
    - Filters by keywords
    - Quota-aware (100 units per call)
    """

    CACHE_TTL = 21600  # 6 hours
    MAX_RETRIES = 2

    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        self.youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        self.quota_manager = YouTubeQuotaManager(redis_client)

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Fetch trending videos from tech categories

        Args:
            config: {'category_ids': [28, 27], 'max_results': 50}
            keywords: Filter by keywords in title/description

        Returns:
            List of trending video articles
        """
        # Check quota before proceeding
        if not await self.quota_manager.check_quota():
            self.logger.warning("YouTube API quota exhausted, skipping trending")
            return []

        category_ids = config.get('category_ids', [28, 27])  # Tech + Education
        max_results = config.get('max_results', 50)

        published_after = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'

        videos = []
        for category_id in category_ids:
            try:
                # API call: search.list (100 units)
                response = self.youtube.search().list(
                    part='snippet',
                    type='video',
                    videoCategoryId=category_id,
                    publishedAfter=published_after,
                    order='viewCount',
                    maxResults=min(max_results, 50),
                    relevanceLanguage='en'
                ).execute()

                # Record quota usage
                await self.quota_manager.record_usage(100)

                # Parse results
                for item in response.get('items', []):
                    video = self._parse_search_result(item)

                    # Filter by keywords
                    if keywords and not self._matches_keywords(video, keywords):
                        continue

                    videos.append(video)

            except Exception as e:
                self.logger.error(f"API error for category {category_id}: {e}")
                continue

        # Deduplicate by video_id
        unique_videos = {v.external_id: v for v in videos}.values()

        self.logger.info(f"Fetched {len(unique_videos)} trending videos")
        return list(unique_videos)[:max_results]

    def _parse_search_result(self, item) -> ScrapedArticle:
        """Parse YouTube API search result to ScrapedArticle"""
        snippet = item['snippet']
        video_id = item['id']['videoId']

        return ScrapedArticle(
            title=snippet['title'],
            url=f"https://www.youtube.com/watch?v={video_id}",
            source_type='youtube_trending',
            external_id=video_id,
            content=snippet['description'],
            author=snippet['channelTitle'],
            published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
            tags=[snippet['channelTitle']],
            raw_data={
                'video_id': video_id,
                'channel_id': snippet['channelId'],
                'thumbnail_url': snippet['thumbnails']['high']['url'],
            }
        )
```

### 3. Quota Manager

**File**: `backend/app/youtube/quota_manager.py`

```python
from datetime import datetime
import redis.asyncio as redis

class YouTubeQuotaManager:
    """Track and enforce YouTube API quota limits"""

    DAILY_LIMIT = 10000  # Free tier
    WARNING_THRESHOLD = 9500  # 95%

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def _get_quota_key(self) -> str:
        """Redis key for today's quota"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        return f"youtube_api_quota:{today}"

    async def check_quota(self) -> bool:
        """Check if quota is available"""
        key = self._get_quota_key()
        usage = await self.redis.get(key)

        if usage is None:
            return True

        current_usage = int(usage)

        if current_usage >= self.WARNING_THRESHOLD:
            logger.warning(f"YouTube quota at {current_usage}/{self.DAILY_LIMIT}")

        return current_usage < self.DAILY_LIMIT

    async def record_usage(self, units: int):
        """Record quota usage"""
        key = self._get_quota_key()
        await self.redis.incrby(key, units)
        await self.redis.expire(key, 86400 * 2)  # Keep for 2 days

    async def get_usage(self) -> int:
        """Get current day's usage"""
        key = self._get_quota_key()
        usage = await self.redis.get(key)
        return int(usage) if usage else 0
```

### 4. Channel Discovery Engine

**File**: `backend/app/youtube/discovery.py`

**Two-Phase Strategy**:

**Phase 1**: Keyword-based scoring (fast, SQL-based)
- Analyze videos from last 30 days
- Calculate match_rate per channel: (matching_videos / total_videos)
- Filter: match_rate > 30% AND total_videos > 5
- Return top 20 candidates

**Phase 2**: Gemini AI ranking (quality filter)
- Analyze channel content quality
- Score relevance to user interests
- Generate explanation for suggestion
- Return top 10 with score > 60

**Implementation**:
```python
import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

class ChannelDiscoveryEngine:
    """AI-powered YouTube channel discovery"""

    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Free tier

    async def discover_channels(self, user_context: Dict) -> List[Dict]:
        """
        Find and rank channel suggestions

        Args:
            user_context: {
                'keywords': List[str],
                'favorite_topics': List[str],
                'read_articles': List[Article]
            }

        Returns:
            List of suggested channels with scores and reasons
        """
        # Phase 1: Find candidates with keyword matching
        candidates = await self._find_candidate_channels(user_context['keywords'])

        if not candidates:
            return []

        # Phase 2: Rank with Gemini AI
        ranked = await self._rank_channels_with_ai(candidates, user_context)

        return ranked

    async def _find_candidate_channels(self, keywords: List[str]) -> List[Dict]:
        """
        Find channels with high keyword match rates

        SQL Strategy:
        1. Get videos from last 30 days
        2. For each video, check if title/tags match keywords
        3. Group by channel_id, calculate match_rate
        4. Filter: match_rate > 30%, total_videos > 5
        5. Exclude already subscribed channels
        """
        # Build keyword matching SQL
        keyword_conditions = " OR ".join([
            f"LOWER(title) LIKE '%{kw.lower()}%'" for kw in keywords
        ])

        query = f"""
        WITH channel_stats AS (
            SELECT
                raw_data->>'channel_id' as channel_id,
                raw_data->>'channel_name' as channel_name,
                COUNT(*) as total_videos,
                SUM(CASE WHEN {keyword_conditions} THEN 1 ELSE 0 END) as matching_videos,
                ROUND(100.0 * SUM(CASE WHEN {keyword_conditions} THEN 1 ELSE 0 END) / COUNT(*), 2) as match_rate,
                ARRAY_AGG(title ORDER BY published_at DESC LIMIT 5) as recent_titles
            FROM articles
            WHERE
                source_type IN ('youtube_rss', 'youtube_trending')
                AND published_at > NOW() - INTERVAL '30 days'
                AND raw_data->>'channel_id' IS NOT NULL
            GROUP BY
                raw_data->>'channel_id',
                raw_data->>'channel_name'
            HAVING
                COUNT(*) >= 5
                AND 100.0 * SUM(CASE WHEN {keyword_conditions} THEN 1 ELSE 0 END) / COUNT(*) > 30
        )
        SELECT *
        FROM channel_stats
        WHERE channel_id NOT IN (
            SELECT channel_id FROM youtube_channels WHERE is_active = TRUE
        )
        ORDER BY match_rate DESC, total_videos DESC
        LIMIT 20;
        """

        result = self.db.execute(query)
        return [dict(row) for row in result]

    async def _rank_channels_with_ai(
        self,
        candidates: List[Dict],
        user_context: Dict
    ) -> List[Dict]:
        """
        Use Gemini to rank channel quality and relevance

        Gemini Free Tier: 15 req/min, 1500 req/day
        Daily discovery: ~20 candidates = well within limits
        """
        ranked_channels = []

        for channel in candidates:
            try:
                # Build prompt
                prompt = f"""
Analyze this YouTube channel for a tech professional interested in: {', '.join(user_context['keywords'])}.

Channel Information:
- Name: {channel['channel_name']}
- Recent video titles:
{chr(10).join(f"  - {title}" for title in channel['recent_titles'])}
- Match rate: {channel['match_rate']}% of videos match user keywords
- Total videos analyzed: {channel['total_videos']}

User's favorite topics: {', '.join(user_context.get('favorite_topics', []))}

Score this channel 0-100 for:
1. Content quality (production value, depth, expertise)
2. Relevance to user's specific interests
3. Consistency and posting frequency
4. Educational value

Return ONLY a JSON object with this exact format:
{{"score": <0-100>, "reason": "<2-3 sentence explanation>"}}
"""

                # Call Gemini API
                response = self.model.generate_content(prompt)
                result_text = response.text.strip()

                # Parse JSON response
                import json
                result = json.loads(result_text)

                # Add to ranked list if score > 60
                if result['score'] >= 60:
                    ranked_channels.append({
                        'channel_id': channel['channel_id'],
                        'channel_name': channel['channel_name'],
                        'match_rate': channel['match_rate'],
                        'total_videos': channel['total_videos'],
                        'suggestion_score': result['score'],
                        'suggestion_reason': result['reason']
                    })

            except Exception as e:
                logger.warning(f"Gemini ranking failed for {channel['channel_name']}: {e}")
                # Fallback: use keyword match_rate as score
                ranked_channels.append({
                    **channel,
                    'suggestion_score': channel['match_rate'],
                    'suggestion_reason': f"Matches {channel['match_rate']}% of your keywords"
                })

        # Sort by score and return top 10
        ranked_channels.sort(key=lambda x: x['suggestion_score'], reverse=True)
        return ranked_channels[:10]
```

### 5. Celery Tasks

**File**: `backend/app/tasks/youtube.py`

```python
from app.tasks.celery_app import celery_app
from app.database import get_db
from app.youtube.discovery import ChannelDiscoveryEngine

@celery_app.task(name='youtube.scrape_rss')
def scrape_youtube_rss():
    """Scrape new videos from YouTube RSS feeds (every 30min)"""
    from app.tasks.scraping import scrape_all_sources_async
    import asyncio

    db = next(get_db())
    try:
        result = asyncio.run(scrape_all_sources_async(
            db=db,
            source_types=['youtube_rss']
        ))
        return result
    finally:
        db.close()

@celery_app.task(name='youtube.scrape_trending')
def scrape_youtube_trending():
    """Scrape trending YouTube videos (every 6 hours)"""
    from app.tasks.scraping import scrape_all_sources_async
    import asyncio

    db = next(get_db())
    try:
        result = asyncio.run(scrape_all_sources_async(
            db=db,
            source_types=['youtube_trending']
        ))
        return result
    finally:
        db.close()

@celery_app.task(name='youtube.discover_channels')
def discover_youtube_channels():
    """Discover and suggest new channels (daily at 2 AM)"""
    import asyncio
    import redis.asyncio as redis
    from app.config import settings

    async def run_discovery():
        db = next(get_db())
        redis_client = await redis.from_url(settings.REDIS_URL)

        try:
            engine = ChannelDiscoveryEngine(db, redis_client)

            # Get user context
            active_keywords = db.query(Keyword).filter_by(is_active=True).all()
            keywords = [kw.keyword for kw in active_keywords]

            # TODO: Build favorite_topics from user's favorited articles
            user_context = {
                'keywords': keywords,
                'favorite_topics': [],  # Populate from analytics
                'read_articles': []
            }

            # Discover channels
            suggestions = await engine.discover_channels(user_context)

            # Save suggestions to database
            for suggestion in suggestions:
                # Check if channel already exists
                existing = db.query(YouTubeChannel).filter_by(
                    channel_id=suggestion['channel_id']
                ).first()

                if not existing:
                    # Create new suggested channel
                    channel = YouTubeChannel(
                        channel_id=suggestion['channel_id'],
                        channel_name=suggestion['channel_name'],
                        channel_url=f"https://www.youtube.com/channel/{suggestion['channel_id']}",
                        rss_feed_url=f"https://www.youtube.com/feeds/videos.xml?channel_id={suggestion['channel_id']}",
                        is_active=False,  # Not active until user accepts
                        is_suggested=True,
                        suggestion_score=suggestion['suggestion_score'],
                        suggestion_reason=suggestion['suggestion_reason']
                    )
                    db.add(channel)

            db.commit()
            logger.info(f"Discovered {len(suggestions)} channel suggestions")

            return {'suggestions': len(suggestions)}

        finally:
            db.close()
            await redis_client.aclose()

    return asyncio.run(run_discovery())
```

**Celery Beat Schedule** (`backend/app/tasks/celery_app.py`):
```python
app.conf.beat_schedule.update({
    'youtube-scrape-rss': {
        'task': 'youtube.scrape_rss',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'youtube-scrape-trending': {
        'task': 'youtube.scrape_trending',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
    'youtube-discover-channels': {
        'task': 'youtube.discover_channels',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
})
```

## Frontend Integration

### 1. Enhanced ArticleCard Component

**File**: `frontend/components/feed/ArticleCard.tsx`

```typescript
import { PlayCircle, Eye, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { formatDuration, formatViews } from '@/lib/utils';

interface ArticleCardProps {
  article: Article;
  onOpenModal: (article: Article) => void;
}

export const ArticleCard = ({ article, onOpenModal }: ArticleCardProps) => {
  // Video-specific rendering
  if (article.is_video) {
    return (
      <div className="article-card video-card border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
        {/* Video Badge */}
        <Badge variant="secondary" className="absolute top-2 right-2 z-10">
          <PlayCircle className="w-3 h-3 mr-1" />
          Video • {formatDuration(article.duration_seconds)}
        </Badge>

        {/* Thumbnail with play overlay */}
        <div
          className="relative cursor-pointer group"
          onClick={() => onOpenModal(article)}
        >
          <img
            src={article.thumbnail_url}
            alt={article.title}
            className="w-full h-48 object-cover"
          />
          <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors flex items-center justify-center">
            <PlayCircle className="w-16 h-16 text-white opacity-80 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>

        {/* Content */}
        <div className="p-4">
          {/* Video metadata */}
          <div className="flex items-center gap-3 text-sm text-muted-foreground mb-2">
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4" />
              {formatViews(article.view_count)}
            </div>
            <span>•</span>
            <span>{article.author}</span>
            <span>•</span>
            <span>{format(new Date(article.published_at), 'MMM dd')}</span>
          </div>

          {/* Title */}
          <h3 className="font-bold text-lg leading-tight mb-2 line-clamp-2">
            {article.title}
          </h3>

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mt-3">
            <Badge variant="outline">{article.category}</Badge>
            {article.tags?.slice(0, 2).map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>

          {/* Score */}
          <div className="mt-3 flex items-center justify-between">
            <Badge variant={article.score > 70 ? 'default' : 'secondary'}>
              Score: {article.score.toFixed(0)}
            </Badge>

            <Button variant="ghost" size="sm">
              Watch Later
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Standard article rendering (existing code)
  return (
    <div className="article-card">
      {/* ... existing article card code ... */}
    </div>
  );
};
```

### 2. Video Preview Modal

**File**: `frontend/components/feed/VideoPreviewModal.tsx`

```typescript
'use client';

import { useModalsStore } from '@/store/modals-store';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, Plus } from 'lucide-react';

export const VideoPreviewModal = () => {
  const { videoModal, closeVideoModal } = useModalsStore();
  const video = videoModal.video;

  if (!video) return null;

  const videoId = video.video_id || extractVideoId(video.url);

  return (
    <Dialog open={videoModal.isOpen} onOpenChange={closeVideoModal}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{video.title}</DialogTitle>
          <DialogDescription className="sr-only">
            Preview YouTube video
          </DialogDescription>
        </DialogHeader>

        {/* Embedded YouTube Player */}
        <div className="aspect-video w-full">
          <iframe
            width="100%"
            height="100%"
            src={`https://www.youtube.com/embed/${videoId}`}
            title={video.title}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>

        {/* Video Info */}
        <div className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="outline">{video.author}</Badge>
              <span className="text-sm text-muted-foreground">
                {formatViews(video.view_count)} views
              </span>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" size="sm" asChild>
                <a
                  href={video.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="w-4 h-4 mr-1" />
                  Watch on YouTube
                </a>
              </Button>

              <Button variant="outline" size="sm">
                <Plus className="w-4 h-4 mr-1" />
                Subscribe to Channel
              </Button>
            </div>
          </div>

          {/* Description */}
          {video.content && (
            <div>
              <h4 className="font-semibold mb-2">Description</h4>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                {video.content}
              </p>
            </div>
          )}

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {video.tags?.map((tag) => (
              <Badge key={tag} variant="secondary">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

function extractVideoId(url: string): string {
  const match = url.match(/[?&]v=([^&]+)/);
  return match ? match[1] : '';
}
```

### 3. Channel Manager Component

**File**: `frontend/components/config/ChannelManager.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useChannels } from '@/hooks/use-channels';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { Plus, Trash2, ExternalLink, Sparkles } from 'lucide-react';

export const ChannelManager = () => {
  const { channels, suggestions, toggleChannel, removeChannel, acceptSuggestion, dismissSuggestion } = useChannels();
  const [addModalOpen, setAddModalOpen] = useState(false);

  const subscribedChannels = channels.filter(c => !c.is_suggested);
  const pendingSuggestions = suggestions.filter(s => s.is_suggested && !s.is_active);

  return (
    <div className="space-y-6">
      {/* Subscribed Channels */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Your Channels ({subscribedChannels.length})</CardTitle>
              <CardDescription>
                YouTube channels you're monitoring for new uploads
              </CardDescription>
            </div>
            <Button onClick={() => setAddModalOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Channel
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {subscribedChannels.map((channel) => (
              <div
                key={channel.id}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  {channel.thumbnail_url && (
                    <img
                      src={channel.thumbnail_url}
                      alt={channel.channel_name}
                      className="w-10 h-10 rounded-full"
                    />
                  )}
                  <div>
                    <div className="font-medium">{channel.channel_name}</div>
                    <div className="text-sm text-muted-foreground">
                      {channel.subscriber_count ?
                        `${formatSubscribers(channel.subscriber_count)} subscribers` :
                        'No stats available'
                      }
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Switch
                    checked={channel.is_active}
                    onCheckedChange={() => toggleChannel(channel.id)}
                  />

                  <Button
                    variant="ghost"
                    size="sm"
                    asChild
                  >
                    <a
                      href={channel.channel_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeChannel(channel.id)}
                  >
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </Button>
                </div>
              </div>
            ))}

            {subscribedChannels.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No channels yet. Add your first channel to get started!
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* AI Suggestions */}
      {pendingSuggestions.length > 0 && (
        <Card className="border-primary/20">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              <CardTitle>Suggested Channels ({pendingSuggestions.length})</CardTitle>
            </div>
            <CardDescription>
              AI-powered recommendations based on your interests
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pendingSuggestions.map((suggestion) => (
                <div
                  key={suggestion.id}
                  className="p-4 border border-primary/30 rounded-lg bg-primary/5"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {suggestion.thumbnail_url && (
                        <img
                          src={suggestion.thumbnail_url}
                          alt={suggestion.channel_name}
                          className="w-12 h-12 rounded-full"
                        />
                      )}
                      <div>
                        <div className="font-medium text-lg">
                          {suggestion.channel_name}
                        </div>
                        <Badge variant="secondary">
                          Score: {suggestion.suggestion_score.toFixed(0)}/100
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground mb-3">
                    {suggestion.suggestion_reason}
                  </p>

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => acceptSuggestion(suggestion.id)}
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Add Channel
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => dismissSuggestion(suggestion.id)}
                    >
                      Dismiss
                    </Button>

                    <Button
                      variant="ghost"
                      size="sm"
                      asChild
                    >
                      <a
                        href={suggestion.channel_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Preview
                      </a>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
```

### 4. FilterBar Updates

**File**: `frontend/components/feed/FilterBar.tsx`

Add video filter toggle:
```typescript
// Add to SOURCES array
const SOURCES = [
  { id: 'hackernews', name: 'HackerNews' },
  { id: 'devto', name: 'Dev.to' },
  { id: 'reddit', name: 'Reddit' },
  { id: 'youtube', name: 'YouTube' },  // NEW
];

// Add "Videos Only" toggle after source pills
<div className="flex items-center gap-2 mt-3">
  <Switch
    id="videos-only"
    checked={activeFilters.videosOnly}
    onCheckedChange={(checked) => setFilters({ videosOnly: checked })}
  />
  <label htmlFor="videos-only" className="text-sm font-medium cursor-pointer">
    Videos Only
  </label>
</div>
```

## Error Handling

### 1. YouTube API Quota Exhaustion

**Problem**: Free tier quota (10,000 units/day) can be exhausted

**Solutions**:
- **Quota tracking**: Redis-based daily usage counter
- **95% threshold warning**: Notify admin when approaching limit
- **Graceful degradation**: Disable trending scraper, continue RSS
- **Retry next day**: Auto-resume when quota resets

### 2. Invalid/Deleted Videos

**Problem**: RSS feeds may include deleted, private, or region-locked videos

**Solutions**:
- **Validation**: HEAD request to check video accessibility
- **Best-effort**: Skip invalid videos, continue scraping
- **Logging**: Track invalid video rate per channel

### 3. RSS Feed Parsing Errors

**Problem**: Malformed XML or unavailable feeds

**Solutions**:
- **feedparser.bozo flag**: Detect malformed feeds
- **Exception handling**: Catch and log parsing errors
- **Channel marking**: Flag problematic channels
- **Retry logic**: Exponential backoff for temporarily unavailable feeds

### 4. Gemini API Failures

**Problem**: Rate limits or API downtime

**Solutions**:
- **Fallback scoring**: Use keyword match_rate if AI unavailable
- **Retry logic**: Exponential backoff for transient errors
- **Graceful degradation**: Still provide suggestions without AI ranking

### 5. Duplicate Videos

**Problem**: Videos can appear in both RSS and trending

**Solutions**:
- **Database constraint**: UNIQUE(source_type='youtube', external_id=video_id)
- **ON CONFLICT**: UPDATE metadata (views, score) instead of INSERT
- **Deduplication**: In-memory set during scraping

## Testing Strategy

### Unit Tests

**test_youtube_scrapers.py**:
```python
import pytest
from app.scrapers.plugins.youtube_rss import YouTubeRSSScraper
from app.scrapers.plugins.youtube_trending import YouTubeTrendingScraper

@pytest.mark.asyncio
async def test_rss_scraper():
    """Test RSS feed parsing"""
    scraper = YouTubeRSSScraper()

    # Test with Google Developers channel
    videos = await scraper.scrape(
        config={'channel_id': 'UC_x5XG1OV2P6uZZ5FSM9Ttw'},
        keywords=['python', 'api']
    )

    assert len(videos) > 0
    assert all(v.video_id for v in videos)
    assert all(v.thumbnail_url for v in videos)
    assert all(v.source_type == 'youtube_rss' for v in videos)

@pytest.mark.asyncio
async def test_trending_scraper_quota_tracking():
    """Test quota usage tracking"""
    scraper = YouTubeTrendingScraper()

    initial_usage = await scraper.quota_manager.get_usage()

    videos = await scraper.scrape(
        config={'category_ids': [28]},
        keywords=['programming']
    )

    final_usage = await scraper.quota_manager.get_usage()
    assert final_usage == initial_usage + 100  # search.list = 100 units

@pytest.mark.asyncio
async def test_discovery_engine():
    """Test channel suggestions"""
    from app.youtube.discovery import ChannelDiscoveryEngine

    engine = ChannelDiscoveryEngine(db, redis)

    user_context = {
        'keywords': ['rust', 'webdev'],
        'favorite_topics': ['systems programming'],
        'read_articles': []
    }

    suggestions = await engine.discover_channels(user_context)

    assert len(suggestions) > 0
    assert all(s['suggestion_score'] >= 60 for s in suggestions)
    assert suggestions[0]['suggestion_score'] >= suggestions[-1]['suggestion_score']
```

### Integration Tests

**test_youtube_integration.py**:
```python
@pytest.mark.asyncio
async def test_full_youtube_flow():
    """End-to-end: subscribe → scrape → display"""
    # 1. Add channel
    channel = await add_youtube_channel(
        channel_id='UC_x5XG1OV2P6uZZ5FSM9Ttw',
        channel_name='Google Developers'
    )
    assert channel.is_active == True

    # 2. Run RSS scraper
    from app.tasks.youtube import scrape_youtube_rss
    result = scrape_youtube_rss.delay()
    result.wait()

    # 3. Verify videos in database
    videos = db.query(Article).filter(
        Article.source_type == 'youtube_rss',
        Article.is_video == True
    ).all()

    assert len(videos) > 0
    assert all(v.video_id for v in videos)

    # 4. Test API endpoint
    response = await client.get('/api/articles?sources=youtube')
    assert response.status_code == 200
    assert response.json()['total'] > 0

@pytest.mark.asyncio
async def test_video_filtering():
    """Test videos-only filter"""
    # Create mix of articles and videos
    db.add(Article(title="Article", url="http://example.com/1", is_video=False))
    db.add(Article(title="Video", url="http://youtube.com/1", is_video=True))
    db.commit()

    # Filter videos only
    response = await client.get('/api/articles?videosOnly=true')
    data = response.json()

    assert all(a['is_video'] for a in data['data'])
```

## Implementation Plan

### Week 1: Core Infrastructure (Jan 6-12)

**Tasks**:
- [ ] Create database migrations
  - `youtube_channels` table
  - `youtube_channel_stats` table
  - Extend `articles` table (video_id, thumbnail_url, duration_seconds, view_count, is_video)
- [ ] Create Pydantic models
  - `ScrapedYouTubeVideo` schema
  - `YouTubeChannelCreate/Response` schemas
- [ ] Implement `YouTubeRSSScraper`
  - RSS feed parsing with feedparser
  - ScrapedArticle conversion
  - Error handling
- [ ] Add unit tests for RSS scraper
- [ ] Set up YouTube API credentials in .env

**Deliverables**:
- Database schema ready
- RSS scraper working and tested
- Can manually add channels and scrape videos

### Week 2: API Integration (Jan 13-19)

**Tasks**:
- [ ] Implement `YouTubeTrendingScraper`
  - YouTube Data API v3 integration
  - Category-based search
  - Keyword filtering
- [ ] Implement `YouTubeQuotaManager`
  - Redis-based quota tracking
  - Warning thresholds
  - Graceful degradation
- [ ] Create Celery tasks
  - `youtube.scrape_rss` (every 30min)
  - `youtube.scrape_trending` (every 6h)
  - Update beat schedule
- [ ] Add integration tests
- [ ] Test with real channels

**Deliverables**:
- Trending scraper working
- Quota management in place
- Automated scraping via Celery

### Week 3: Discovery Engine (Jan 20-26)

**Tasks**:
- [ ] Set up Gemini API
  - Get API key
  - Configure SDK
- [ ] Implement `ChannelDiscoveryEngine`
  - SQL-based candidate finding
  - Gemini AI ranking
  - Suggestion storage
- [ ] Create Celery task
  - `youtube.discover_channels` (daily at 2 AM)
- [ ] Add discovery tests
- [ ] Test suggestion quality

**Deliverables**:
- Discovery engine working
- Daily channel suggestions
- AI ranking validated

### Week 4: Frontend (Jan 27 - Feb 2)

**Tasks**:
- [ ] Update `ArticleCard` for video display
  - Video badge
  - Thumbnail with play overlay
  - Video metadata (views, duration)
- [ ] Create `VideoPreviewModal`
  - Embedded YouTube player
  - Channel subscribe button
- [ ] Build `ChannelManager` component
  - Subscribed channels list
  - AI suggestions section
  - Add/remove channels
- [ ] Update `FilterBar`
  - Add YouTube to sources
  - Add "Videos Only" toggle
- [ ] Create backend API endpoints
  - `GET/POST /api/youtube/channels`
  - `POST /api/youtube/channels/:id/accept`
  - `POST /api/youtube/channels/:id/dismiss`
- [ ] End-to-end testing

**Deliverables**:
- Full UI for YouTube integration
- Video cards in feed
- Channel management interface
- Complete feature ready for production

## Dependencies

**Backend** (`pyproject.toml`):
```toml
[tool.poetry.dependencies]
feedparser = "^6.0.10"  # RSS parsing
google-api-python-client = "^2.108.0"  # YouTube Data API v3
google-auth = "^2.25.0"  # YouTube API auth
google-generativeai = "^0.3.0"  # Gemini API
```

**Frontend** (`package.json`):
```json
{
  "dependencies": {
    "lucide-react": "^0.x.x"  // Already installed - for PlayCircle, Eye icons
  }
}
```

## API Endpoints

### Backend Routes

**File**: `backend/app/api/youtube.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.youtube_channel import YouTubeChannel

router = APIRouter()

@router.get("/youtube/channels")
async def get_youtube_channels(
    include_suggestions: bool = True,
    db: Session = Depends(get_db)
):
    """Get all YouTube channels (subscribed + suggestions)"""
    query = db.query(YouTubeChannel)

    if not include_suggestions:
        query = query.filter(YouTubeChannel.is_active == True)

    channels = query.order_by(
        YouTubeChannel.is_active.desc(),
        YouTubeChannel.suggestion_score.desc()
    ).all()

    return {"channels": channels}

@router.post("/youtube/channels")
async def add_youtube_channel(
    channel_data: Dict,
    db: Session = Depends(get_db)
):
    """Manually add a YouTube channel"""
    channel_id = channel_data.get('channel_id')

    # Check if already exists
    existing = db.query(YouTubeChannel).filter_by(channel_id=channel_id).first()
    if existing:
        raise HTTPException(400, "Channel already exists")

    # Create channel
    channel = YouTubeChannel(
        channel_id=channel_id,
        channel_name=channel_data['channel_name'],
        channel_url=f"https://www.youtube.com/channel/{channel_id}",
        rss_feed_url=f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
        is_active=True,
        is_suggested=False
    )

    db.add(channel)
    db.commit()
    db.refresh(channel)

    return channel

@router.post("/youtube/channels/{channel_id}/accept")
async def accept_suggested_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """Accept an AI-suggested channel"""
    channel = db.query(YouTubeChannel).filter_by(id=channel_id).first()

    if not channel:
        raise HTTPException(404, "Channel not found")

    channel.is_active = True
    db.commit()

    return {"message": "Channel accepted"}

@router.delete("/youtube/channels/{channel_id}")
async def remove_youtube_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """Remove or dismiss a channel"""
    channel = db.query(YouTubeChannel).filter_by(id=channel_id).first()

    if not channel:
        raise HTTPException(404, "Channel not found")

    db.delete(channel)
    db.commit()

    return {"message": "Channel removed"}
```

## Success Metrics

### Technical Metrics
- **RSS scraper reliability**: > 99% success rate
- **API quota usage**: < 95% of daily limit
- **Discovery quality**: > 70% suggestion acceptance rate
- **Video deduplication**: 100% (no duplicate videos)
- **Performance**: < 2s for video preview modal load

### User Metrics
- **Channel adoption**: Users subscribe to 5+ channels within first week
- **Video engagement**: > 50% of users watch at least 1 video/day
- **Suggestion acceptance**: > 30% of AI suggestions accepted
- **Feed diversity**: Videos represent 20-30% of feed content

## Future Enhancements

### Phase 2 (After Initial Launch)
1. **Playlist support** - Track specific YouTube playlists
2. **Watch history** - Track watched videos, suggest based on history
3. **Video transcripts** - Use YouTube transcript API for better search
4. **Live stream alerts** - Notify when followed channels go live
5. **Video collections** - User-curated playlists/collections

### Phase 3 (Advanced)
6. **AI video summarization** - Generate summaries of video content
7. **Key moments extraction** - Identify important timestamps
8. **Related video suggestions** - ML-based recommendations
9. **Cross-platform integration** - Link related articles/videos
10. **Community features** - Share videos, collaborative playlists

## References

- [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3)
- [YouTube RSS Feeds](https://support.google.com/youtube/answer/6224202)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [feedparser Documentation](https://feedparser.readthedocs.io/)
- [Project Architecture](./2026-01-02-scraper-architecture-design.md)

---

**Status**: Design Complete - Ready for Implementation
**Next Step**: Begin Week 1 implementation (database migrations)
**Last Updated**: 2026-01-03
