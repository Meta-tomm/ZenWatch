# Component Hierarchy

## Home Page (`/`)

```
app/page.tsx
├── AnimatedTitle (title="ZENWATCH", subtitle="...")
├── Grid (2 columns on desktop)
│   ├── BestArticleCard
│   │   ├── CornerBrackets (color="yellow")
│   │   ├── Trophy icon
│   │   ├── Article content
│   │   ├── LikeDislikeButtons
│   │   └── Action buttons (favorite, bookmark, read)
│   └── BestVideoCard
│       ├── CornerBrackets (color="blue")
│       ├── Trophy icon
│       ├── Video thumbnail
│       ├── Video content
│       ├── LikeDislikeButtons
│       └── Action buttons (favorite, watch)
└── StatsPlaceholder
    ├── CornerBrackets (color="green")
    └── Placeholder metrics (3 cards)
```

## Research Page (`/articles`)

```
app/articles/page.tsx
├── Header
│   └── Back button + Title ("Research Hub")
├── FilterBar
│   └── (existing filters)
├── Flex Container (2 columns)
│   ├── ArticleFeed (main area, flex-1)
│   │   └── Virtuoso
│   │       └── ArticleCard[] (multiple)
│   │           ├── CornerBrackets (color based on score)
│   │           ├── Article header
│   │           ├── Tags
│   │           ├── Summary
│   │           ├── Stats (upvotes, comments)
│   │           ├── LikeDislikeButtons (NEW)
│   │           └── Action buttons
│   └── VideoPanel (sidebar, w-80/96)
│       ├── Header (sticky)
│       └── ScrollArea
│           └── VideoPreview[] (compact mode)
│               ├── Thumbnail
│               ├── Play overlay
│               ├── Duration badge
│               ├── Video info
│               ├── LikeDislikeButtons
│               └── Action buttons
└── ArticleModal
    └── (existing modal)
```

## Component Dependencies

### LikeDislikeButtons
**Used by:**
- BestArticleCard
- BestVideoCard
- ArticleCard
- VideoPreview

**Props:**
```typescript
{
  initialLikes?: number;
  initialDislikes?: number;
  userReaction?: 'like' | 'dislike' | null;
  onLike?: () => void;
  onDislike?: () => void;
  size?: 'sm' | 'md' | 'lg';
  showCounts?: boolean;
}
```

### VideoPreview
**Used by:**
- VideoPanel
- (Future: Home page grid)

**Props:**
```typescript
{
  video: Video;
  onToggleFavorite?: (id: string) => void;
  compact?: boolean;
}
```

**Modes:**
- `compact={true}` - Used in sidebar (smaller, less detail)
- `compact={false}` - Full preview with all details

### CornerBrackets
**Used by:**
- ArticleCard
- BestArticleCard
- BestVideoCard
- StatsPlaceholder

**Colors:**
- `green` - Default, stats placeholder
- `yellow` - Best article, high scores
- `blue` - Best video, medium scores

## Data Flow

### Home Page
```
BestArticleCard
  └─> articlesApi.getBestOfWeek()
      └─> GET /api/articles/best-of-week
          └─> Returns Article | null

BestVideoCard
  └─> videosApi.getBestOfWeek()
      └─> GET /api/videos/best-of-week
          └─> Returns Video | null
```

### Research Page
```
ArticleFeed
  └─> useArticles(filters)
      └─> articlesApi.getArticles(params)
          └─> GET /api/articles?...
              └─> Returns PaginatedResponse<Article>

VideoPanel
  └─> videosApi.getVideos({ sort: 'score', limit: 10 })
      └─> GET /api/videos?sort=score&limit=10
          └─> Returns PaginatedResponse<Video>
```

### Like/Dislike Flow
```
User clicks thumbs up/down
  └─> LikeDislikeButtons
      └─> Optimistic UI update (instant)
      └─> onLike() / onDislike() callback
          └─> Parent component
              └─> articlesApi.toggleLike(id) OR
                  videosApi.toggleLike(id)
                  └─> POST /api/articles/:id/like OR
                      POST /api/videos/:id/like
                      └─> Returns updated Article/Video
                          └─> Parent updates local state
```

## State Management

### Local State
- **BestArticleCard:** `useState<Article | null>`
- **BestVideoCard:** `useState<Video | null>`
- **VideoPanel:** `useState<Video[]>`
- **ArticleCard:** `useState<Article>` (localArticle)
- **LikeDislikeButtons:** `useState` for optimistic updates

### TanStack Query
- **ArticleFeed:** `useArticles(filters)` - Infinite query with pagination
- No video hooks yet (VideoPanel uses direct API calls)

### UI Store (Zustand)
- Filter state (existing)
- Modal state (existing)

## Responsive Breakpoints

```
Mobile (< 768px)
- Home: Single column (stacked)
- Research: Video panel hidden

Tablet (768px - 1024px)
- Home: 2 columns if space allows
- Research: Video panel visible (320px)

Desktop (1024px+)
- Home: 2 columns
- Research: Video panel visible (384px on xl)
```

## File Sizes (Production Build)

```
Home page:        6.84 kB (+ 166 kB shared)
Articles page:   29.3 kB  (+ 244 kB shared)
Config page:     34.4 kB  (+ 194 kB shared)
```

## Performance Considerations

### Optimizations Applied
1. **Virtuoso** for article list (only renders visible items)
2. **Lazy loading** via TanStack Query pagination
3. **Optimistic updates** for like/dislike (no waiting)
4. **Image lazy loading** for video thumbnails
5. **Responsive hiding** of video panel on mobile

### Future Optimizations
1. Add TanStack Query for VideoPanel
2. Implement video thumbnail lazy loading
3. Add intersection observer for video previews
4. Memoize expensive calculations
5. Add service worker for offline support

---

**Component Count:**
- New Components: 6
- Updated Components: 2
- New Type Definitions: 1
- New API Methods: 8
