# Library & Triage Feature Design

**Date**: 2026-01-06
**Status**: Approved
**Author**: Brainstorming session

---

## Overview

Two new features for ZenWatch:

- **Library**: A "read later" collection. Items persist until manually removed. Shows read/unread state. Toggle between list and grid view.
- **Triage**: A swipe-based discovery page. Personalized random articles weighted by user keywords. Swipe right = add to Library, swipe left = dismiss from Triage (still visible in Feed).

### Key Distinctions

| Feature | Purpose |
|---------|---------|
| Favorite (Star) | "I loved this" - permanent collection of great content |
| Bookmark (Library) | "Read later" - temporary queue for items to check |

---

## Data Model

### Database Changes

Add three fields to the `articles` table:

```sql
ALTER TABLE articles ADD COLUMN is_bookmarked BOOLEAN DEFAULT FALSE;
ALTER TABLE articles ADD COLUMN is_dismissed BOOLEAN DEFAULT FALSE;
ALTER TABLE articles ADD COLUMN bookmarked_at TIMESTAMP NULL;
```

| Field | Purpose |
|-------|---------|
| `is_bookmarked` | Item is in Library |
| `is_dismissed` | Hidden from Triage only (still shows in Feed) |
| `bookmarked_at` | When added to Library (for sorting) |

Existing `is_read` field indicates if user has opened the item from Library.

---

## API Endpoints

### Library Endpoints

```
GET    /api/library                     # Get bookmarked items
POST   /api/articles/{id}/bookmark      # Toggle bookmark
```

**GET /api/library**
- Query params: `type` (all|article|video), `unread_only` (bool)
- Returns: List of bookmarked articles, sorted by `bookmarked_at` DESC

**POST /api/articles/{id}/bookmark**
- Toggle `is_bookmarked`, set/clear `bookmarked_at`
- Returns: Updated article

### Triage Endpoints

```
GET    /api/triage                      # Get next items for triage
POST   /api/articles/{id}/dismiss       # Mark as dismissed
```

**GET /api/triage?limit=10**
- Algorithm:
  1. Filter out: `is_bookmarked`, `is_dismissed`, `is_archived`, `is_read`
  2. Get user's active keywords with weights
  3. Score-weighted random selection:
     - 70% from articles with score >= 50
     - 30% from articles with score < 50 (discovery)
  4. Shuffle and return batch
- Returns: List of articles for triage

**POST /api/articles/{id}/dismiss**
- Set `is_dismissed=True`
- Returns: `{success: true}`

---

## Library Page

**Route**: `/library`

### UI Layout

```
+-----------------------------------------------------+
|  Library                        [List] [Grid]       |
|  12 items saved                                     |
|----------------------------------------------------|
|  Filter: [All]  [Articles] [Videos]  [Unread]      |
|----------------------------------------------------|
|                                                     |
|  +-------------+  +-------------+  +-------------+ |
|  | * Article 1 |  | o Article 2 |  | > Video 1   | |
|  |   unread    |  |   read      |  |   unread    | |
|  |   [Remove]  |  |   [Remove]  |  |   [Remove]  | |
|  +-------------+  +-------------+  +-------------+ |
|                                                     |
+-----------------------------------------------------+
```

### Features

- **View toggle**: List (compact) or Grid (visual cards)
- **Filters**: All, Articles only, Videos only, Unread only
- **Visual indicators**: Dot/badge for unread items, video icon for videos
- **Actions per item**: Open (marks as read), Remove from Library, Open external link
- **Sort**: By date added (newest first)
- **Empty state**: "Your library is empty. Add items from the Feed or try Triage mode."

### State Management

- `useLibrary` hook using TanStack Query
- Optimistic updates for remove action
- Persist view preference (list/grid) in localStorage

---

## Triage Page

**Route**: `/triage`

### UI Layout

```
+-----------------------------------------------------+
|  Triage                              [Exit]         |
|  Discover new content                               |
|----------------------------------------------------|
|                                                     |
|         +---------------------------+               |
|    <-   |                           |    ->         |
|  SKIP   |      Article Card         |   SAVE        |
|         |                           |               |
|         |   Title                   |               |
|         |   Source - 5 min - 72     |               |
|         |   [Tags]                  |               |
|         |                           |               |
|         |   Summary preview...      |               |
|         |                           |               |
|         |      [Tap for more]       |               |
|         |                           |               |
|         +---------------------------+               |
|                                                     |
|              <- Swipe left    Swipe right ->        |
|                 (dismiss)      (library)            |
|                                                     |
+-----------------------------------------------------+
```

### Interactions

- **Swipe right**: Add to Library, show next card with success feedback
- **Swipe left**: Mark as dismissed, show next card
- **Tap card**: Expand modal with full details (summary, content preview, external link)
- **Swipe in modal**: Not allowed - must close modal first to swipe

### Triage Algorithm

```python
# Backend: GET /api/triage?limit=10
- Exclude: is_bookmarked=True, is_dismissed=True, is_archived=True
- Weight by: user's keyword scores (higher score = more likely to appear)
- Mix: 70% high-score articles, 30% random from lower scores (discovery)
- Return batch of 10, frontend shows one at a time
```

### Empty State

"All caught up! No new items to triage."

---

## Frontend Components

### New Files Structure

```
frontend/
├── app/
│   ├── library/
│   │   └── page.tsx              # Library page
│   └── triage/
│       └── page.tsx              # Triage page
│
├── components/
│   ├── library/
│   │   ├── LibraryGrid.tsx       # Grid view
│   │   ├── LibraryList.tsx       # List view
│   │   ├── LibraryCard.tsx       # Card for grid
│   │   ├── LibraryItem.tsx       # Row for list
│   │   └── LibraryFilters.tsx    # Filter bar
│   │
│   └── triage/
│       ├── TriageCard.tsx        # Swipeable card
│       ├── TriageStack.tsx       # Card stack manager
│       ├── SwipeIndicators.tsx   # Left/right visual hints
│       └── TriageModal.tsx       # Expanded detail view
│
├── hooks/
│   ├── useLibrary.ts             # TanStack Query for library
│   ├── useTriage.ts              # TanStack Query for triage
│   └── useSwipeGesture.ts        # Framer Motion swipe logic
│
└── types/
    └── index.ts                  # Add BookmarkResponse, TriageItem
```

### Dependencies

- `framer-motion` (already installed) - for swipe gestures and card animations
- No new dependencies needed

### Sidebar Update

Add to `navItems` in `Sidebar.tsx`:

```typescript
import { Bookmark, Shuffle } from 'lucide-react';

const navItems = [
  { href: '/', icon: Home, label: 'Feed' },
  { href: '/articles', icon: FileText, label: 'Articles' },
  { href: '/library', icon: Bookmark, label: 'Library' },      // NEW
  { href: '/triage', icon: Shuffle, label: 'Triage' },         // NEW
  { href: '/config', icon: Settings, label: 'Configuration' },
  { href: '/analytics', icon: BarChart3, label: 'Analytics' },
];
```

---

## Backend Structure

### New Files

```
backend/app/
├── api/
│   ├── library.py                # Library endpoints
│   └── triage.py                 # Triage endpoints
│
└── schemas/
    ├── library.py                # LibraryResponse
    └── triage.py                 # TriageResponse
```

### Schemas

```python
# schemas/library.py
class LibraryResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    unread_count: int

# schemas/triage.py
class TriageResponse(BaseModel):
    items: list[ArticleResponse]
    remaining_count: int  # How many more to triage
```

### Router Registration

Add to `main.py`:

```python
from app.api import library, triage

app.include_router(library.router, prefix="/api", tags=["library"])
app.include_router(triage.router, prefix="/api", tags=["triage"])
```

---

## Wiring Existing UI

### ArticleCard Update

The `BookmarkPlus` button already exists. Wire it up:

```typescript
// In ArticleCard.tsx
const toggleBookmark = useToggleBookmark();

<Button
  variant="ghost"
  size="sm"
  onClick={() => toggleBookmark.mutate(localArticle.id)}
>
  <BookmarkPlus
    className={cn(
      "w-4 h-4",
      localArticle.is_bookmarked && "fill-violet-400 text-violet-400"
    )}
  />
</Button>
```

Same pattern for `VideoPreview` and `BestVideoCard3D` components.

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Bookmark from Triage | Add to library + auto-advance to next card |
| Dismiss from Library | Remove from library (toggle off is_bookmarked) |
| Article already read | Still shows in Triage (user might want to save it) |
| No items for Triage | Show empty state with link to Feed |
| Offline/error | Optimistic update, rollback on failure, toast error |

---

## Success Feedback

- **Bookmark added**: Brief toast "Added to Library"
- **Swipe right in Triage**: Card flies right + subtle checkmark animation
- **Swipe left in Triage**: Card flies left + fade out

---

## Content Types

Both articles and videos are handled together in a unified experience. The `is_video` field in the Article model distinguishes them visually with appropriate icons.
