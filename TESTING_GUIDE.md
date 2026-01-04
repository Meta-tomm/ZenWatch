# Frontend Testing Guide

## Quick Start

### 1. Start the Development Server

```bash
cd /home/chapuis/Documents/ZenWatch/frontend
npm run dev
```

The app will be available at `http://localhost:3000`

### 2. Test Home Page

**URL:** `http://localhost:3000/`

**Expected Behavior:**
- Animated "ZENWATCH" title with glitch effect
- Two cards side-by-side (desktop) or stacked (mobile):
  - Article of the Week (yellow border)
  - Video of the Week (blue border)
- Stats placeholder section with animated icons
- Like/dislike buttons on both cards

**Known Issues Without Backend:**
- Cards will show "No articles/videos available"
- API calls will fail (expected)

### 3. Test Research Page

**URL:** `http://localhost:3000/articles`

**Expected Behavior:**
- Header shows "Research Hub" with back button
- Filter bar at top
- Two-column layout (desktop):
  - Left: Scrollable article feed
  - Right: Video panel with top videos
- Video panel hidden on mobile
- Like/dislike buttons on each article card

**Known Issues Without Backend:**
- Articles may load if backend is running
- Video panel will show "Failed to load videos"

## Component Testing Checklist

### LikeDislikeButtons

**Test Cases:**
1. Click thumbs up - count should increase, icon fills
2. Click thumbs up again - count decreases, icon unfills
3. Click thumbs down - count increases, icon fills
4. Switch from like to dislike - both counts update correctly
5. Visual feedback matches action (green for like, red for dislike)

**Test with:**
```javascript
// In browser console
// Should see optimistic updates
```

### BestArticleCard

**Test Cases:**
1. Loads best article from API
2. Shows loading skeleton while fetching
3. Shows error message if API fails
4. Displays score, tags, summary
5. Like/dislike buttons work
6. Favorite button toggles
7. "Read Article" button opens in new tab

### BestVideoCard

**Test Cases:**
1. Loads best video from API
2. Shows loading skeleton while fetching
3. Shows error message if API fails
4. Video thumbnail displays (or placeholder)
5. Play icon appears on hover
6. Duration badge shows in bottom-right
7. Score badge shows in top-right
8. Like/dislike buttons work
9. "Watch Video" button opens in new tab

### VideoPanel

**Test Cases:**
1. Loads top 10 videos sorted by score
2. Shows loading skeletons while fetching
3. Shows error message if API fails
4. Videos display in compact mode
5. Scroll works for long lists
6. Favorite button on each video works
7. External link button opens video

### VideoPreview

**Compact Mode Test:**
1. Smaller thumbnail (aspect-video)
2. 2-line title truncation
3. Condensed info
4. Smaller action buttons

**Full Mode Test:**
1. Larger thumbnail
2. Full summary visible
3. All tags shown
4. Full action buttons

## Mock Data Testing

To test without backend, create mock API responses:

### Option 1: Mock Service Worker

Create `frontend/mocks/handlers.ts`:

```typescript
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/articles/best-of-week', () => {
    return HttpResponse.json({
      id: '1',
      title: 'Mock Article of the Week',
      url: 'https://example.com',
      summary: 'This is a mock article for testing...',
      score: 95,
      category: 'AI',
      tags: ['machine-learning', 'gpt-4'],
      source_type: 'reddit',
      published_at: new Date().toISOString(),
      upvotes: 1500,
      comments_count: 234,
      is_favorite: false,
      is_read: false,
      is_archived: false,
      likes: 42,
      dislikes: 3,
      user_reaction: null,
    });
  }),

  http.get('/api/videos/best-of-week', () => {
    return HttpResponse.json({
      id: '1',
      title: 'Mock Video of the Week',
      url: 'https://youtube.com/watch?v=dQw4w9WgXcQ',
      video_url: 'https://youtube.com/watch?v=dQw4w9WgXcQ',
      video_id: 'dQw4w9WgXcQ',
      platform: 'youtube',
      summary: 'This is a mock video for testing...',
      score: 88,
      category: 'Tutorial',
      tags: ['react', 'typescript'],
      source_type: 'youtube',
      published_at: new Date().toISOString(),
      duration_minutes: 15,
      views: 50000,
      is_favorite: false,
      likes: 120,
      dislikes: 5,
      user_reaction: null,
    });
  }),

  http.get('/api/videos', () => {
    const videos = Array.from({ length: 10 }, (_, i) => ({
      id: String(i + 1),
      title: `Test Video ${i + 1}`,
      url: `https://youtube.com/watch?v=test${i}`,
      video_url: `https://youtube.com/watch?v=test${i}`,
      video_id: `test${i}`,
      platform: 'youtube' as const,
      score: 90 - i * 5,
      category: 'Tech',
      tags: ['test'],
      source_type: 'youtube',
      published_at: new Date().toISOString(),
      duration_minutes: 10,
      views: 1000,
      is_favorite: false,
      likes: 10,
      dislikes: 1,
    }));

    return HttpResponse.json({
      data: videos,
      total: 10,
      hasMore: false,
    });
  }),
];
```

### Option 2: API Mock in Components

Temporarily modify components to return mock data:

```typescript
// In BestArticleCard.tsx
useEffect(() => {
  const fetchBestArticle = async () => {
    try {
      setIsLoading(true);
      // Mock data instead of API call
      const mockArticle = {
        id: '1',
        title: 'Test Article of the Week',
        // ... rest of mock data
      };
      setArticle(mockArticle);
      setError(null);
    } finally {
      setIsLoading(false);
    }
  };

  fetchBestArticle();
}, []);
```

## Visual Testing Checklist

### Home Page

- [ ] Title animation plays on load
- [ ] Cards have proper spacing
- [ ] Yellow border on article card
- [ ] Blue border on video card
- [ ] Stats placeholder shows animated icons
- [ ] Layout responsive (stacks on mobile)
- [ ] All text readable
- [ ] Scores display prominently

### Research Page

- [ ] Header sticky on scroll
- [ ] Filter bar accessible
- [ ] Article feed scrolls smoothly
- [ ] Video panel fixed on right
- [ ] Video panel scrolls independently
- [ ] Like/dislike buttons aligned properly
- [ ] Cards have hover effects
- [ ] Video thumbnails load (or show placeholder)

### Responsive Testing

**Desktop (1920x1080):**
- [ ] Home: Two columns side-by-side
- [ ] Research: Video panel 384px wide
- [ ] All content readable
- [ ] No overflow issues

**Tablet (768x1024):**
- [ ] Home: Two columns if space
- [ ] Research: Video panel 320px wide
- [ ] Touch targets adequate size
- [ ] Navigation accessible

**Mobile (375x667):**
- [ ] Home: Single column stacked
- [ ] Research: Video panel hidden
- [ ] Article cards full width
- [ ] Filter bar usable
- [ ] Bottom nav visible

## Performance Testing

### Lighthouse Scores (Target)

```
Performance: > 90
Accessibility: > 95
Best Practices: > 90
SEO: > 90
```

### Load Time Testing

```bash
# Build production version
npm run build
npm run start

# Test with Chrome DevTools:
# - Network tab: Disable cache
# - Performance tab: Record page load
```

**Targets:**
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Time to Interactive: < 3.5s
- Cumulative Layout Shift: < 0.1

## Browser Testing

Test in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

## Known Issues & Workarounds

### Issue 1: API Calls Fail
**Cause:** Backend not running or endpoints not implemented
**Workaround:** Use mock data (see above)
**Status:** Expected until backend is implemented

### Issue 2: Video Thumbnails Don't Load
**Cause:** Invalid video URLs or network issues
**Workaround:** Falls back to `/placeholder-video.png`
**Fix:** Add placeholder image or use valid YouTube URLs

### Issue 3: Like/Dislike State Not Persisted
**Cause:** Backend endpoints not implemented
**Workaround:** Optimistic UI still works, just not saved
**Status:** Expected until backend is implemented

### Issue 4: Video Panel Empty
**Cause:** No videos in database
**Workaround:** Add mock videos or use mock data
**Status:** Expected until video scraping is implemented

## Debugging Tips

### Enable Debug Logging

Add to `.env.local`:
```
NEXT_PUBLIC_DEBUG=true
```

### Check Network Requests

```javascript
// In browser console
// Watch for API calls
window.addEventListener('fetch', (e) => {
  console.log('Fetch:', e.request.url);
});
```

### Check Component State

Use React DevTools:
1. Install React DevTools extension
2. Open DevTools > Components tab
3. Select component
4. View props and state

### Check Console Errors

Open browser console (F12) and look for:
- API errors (red)
- Component errors (red)
- Warnings (yellow)

## Success Criteria

Frontend is working correctly if:

1. ✅ Build completes without errors
2. ✅ Home page renders without crashes
3. ✅ Research page renders without crashes
4. ✅ All components display properly
5. ✅ Like/dislike buttons are interactive
6. ✅ Responsive layout works
7. ✅ No console errors (except expected API failures)
8. ✅ All links work
9. ✅ Navigation works
10. ✅ Lighthouse score > 90

---

**Next Steps:**
1. Start backend development for video support
2. Implement like/dislike endpoints
3. Add authentication for user reactions
4. Integrate Power BI dashboard
5. Add video scraping workers
