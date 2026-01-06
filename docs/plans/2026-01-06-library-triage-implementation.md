# Library & Triage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a "read later" Library and swipe-based Triage page to ZenWatch.

**Architecture:** Backend adds 3 new fields to articles table, 2 new API routers. Frontend adds 2 new pages, hooks, and components using existing patterns (TanStack Query, Framer Motion for swipe).

**Tech Stack:** FastAPI, SQLAlchemy, Alembic (backend) | Next.js 14, TypeScript, TanStack Query, Framer Motion (frontend)

---

## Phase 1: Backend Database & Model

### Task 1: Create Alembic Migration

**Files:**
- Create: `backend/alembic/versions/xxxx_add_library_triage_fields.py`

**Step 1: Generate migration file**

Run:
```bash
cd backend && poetry run alembic revision -m "add_library_triage_fields"
```

**Step 2: Edit migration with upgrade/downgrade**

```python
"""add_library_triage_fields

Revision ID: <generated>
Revises: 017d00fa9777
Create Date: 2026-01-06
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '<generated>'
down_revision = '017d00fa9777'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('articles', sa.Column('is_bookmarked', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('articles', sa.Column('is_dismissed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('articles', sa.Column('bookmarked_at', sa.DateTime(), nullable=True))

    # Index for library queries (bookmarked items sorted by date)
    op.create_index('idx_articles_bookmarked', 'articles', ['is_bookmarked', 'bookmarked_at'])
    # Index for triage queries (exclude bookmarked/dismissed)
    op.create_index('idx_articles_triage', 'articles', ['is_bookmarked', 'is_dismissed', 'is_archived'])


def downgrade() -> None:
    op.drop_index('idx_articles_triage', table_name='articles')
    op.drop_index('idx_articles_bookmarked', table_name='articles')
    op.drop_column('articles', 'bookmarked_at')
    op.drop_column('articles', 'is_dismissed')
    op.drop_column('articles', 'is_bookmarked')
```

**Step 3: Run migration**

Run:
```bash
cd backend && poetry run alembic upgrade head
```
Expected: Migration applies successfully

**Step 4: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat(db): add library and triage fields to articles"
```

---

### Task 2: Update Article Model

**Files:**
- Modify: `backend/app/models/article.py:59-66`

**Step 1: Add new fields to Article model**

After line 66 (`is_video = Column(...)`), add:

```python
    # Library & Triage fields
    is_bookmarked = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    bookmarked_at = Column(DateTime, nullable=True)
```

**Step 2: Verify model loads**

Run:
```bash
cd backend && poetry run python -c "from app.models import Article; print('OK')"
```
Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/models/article.py
git commit -m "feat(model): add is_bookmarked, is_dismissed, bookmarked_at to Article"
```

---

### Task 3: Update Article Schema

**Files:**
- Modify: `backend/app/schemas/article.py:38-51`

**Step 1: Add new fields to ArticleResponse**

After line 51 (`is_video: Optional[bool] = False`), add:

```python
    is_bookmarked: bool = False
    is_dismissed: bool = False
    bookmarked_at: Optional[datetime] = None
```

**Step 2: Verify schema**

Run:
```bash
cd backend && poetry run python -c "from app.schemas.article import ArticleResponse; print('OK')"
```
Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/schemas/article.py
git commit -m "feat(schema): add library fields to ArticleResponse"
```

---

## Phase 2: Backend API Endpoints

### Task 4: Create Library Router

**Files:**
- Create: `backend/app/api/library.py`

**Step 1: Write the library router**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models import Article, Source
from app.schemas.article import ArticleResponse
from app.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)
router = APIRouter()


class LibraryResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    unread_count: int


@router.get("/library", response_model=LibraryResponse)
async def get_library(
    type: Optional[str] = Query(None, pattern="^(all|article|video)$"),
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all bookmarked items (Library)"""
    query = db.query(Article).options(joinedload(Article.source)).filter(
        Article.is_bookmarked == True
    )

    # Filter by type
    if type == "article":
        query = query.filter(Article.is_video == False)
    elif type == "video":
        query = query.filter(Article.is_video == True)

    # Filter unread only
    if unread_only:
        query = query.filter(Article.is_read == False)

    # Get total and unread counts
    total = query.count()
    unread_count = query.filter(Article.is_read == False).count() if not unread_only else total

    # Sort by bookmarked_at descending (newest first)
    items = query.order_by(Article.bookmarked_at.desc()).limit(limit).offset(offset).all()

    # Transform to response
    items_data = []
    for item in items:
        item_dict = {
            **item.__dict__,
            'source_type': item.source.type if item.source else None
        }
        items_data.append(ArticleResponse.model_validate(item_dict))

    logger.info(f"Retrieved {len(items)} library items (total: {total}, unread: {unread_count})")

    return LibraryResponse(
        items=items_data,
        total=total,
        unread_count=unread_count
    )


@router.post("/articles/{article_id}/bookmark", response_model=ArticleResponse)
async def toggle_bookmark(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Toggle bookmark status on an article"""
    article = db.query(Article).options(joinedload(Article.source)).filter(
        Article.id == article_id
    ).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Toggle bookmark
    if article.is_bookmarked:
        article.is_bookmarked = False
        article.bookmarked_at = None
        logger.info(f"Article {article_id} removed from library")
    else:
        article.is_bookmarked = True
        article.bookmarked_at = datetime.utcnow()
        logger.info(f"Article {article_id} added to library")

    db.commit()
    db.refresh(article)

    article_dict = {
        **article.__dict__,
        'source_type': article.source.type if article.source else None
    }
    return ArticleResponse.model_validate(article_dict)
```

**Step 2: Verify syntax**

Run:
```bash
cd backend && poetry run python -c "from app.api.library import router; print('OK')"
```
Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/api/library.py
git commit -m "feat(api): add library endpoints"
```

---

### Task 5: Create Triage Router

**Files:**
- Create: `backend/app/api/triage.py`

**Step 1: Write the triage router**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import Article, Source
from app.schemas.article import ArticleResponse
from app.utils.logger import get_logger
from pydantic import BaseModel
import random

logger = get_logger(__name__)
router = APIRouter()


class TriageResponse(BaseModel):
    items: list[ArticleResponse]
    remaining_count: int


@router.get("/triage", response_model=TriageResponse)
async def get_triage_items(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get items for triage (swipe interface).

    Algorithm:
    - Exclude: is_bookmarked, is_dismissed, is_archived
    - 70% high-score articles (score >= 50)
    - 30% discovery articles (score < 50 or null)
    - Randomized within each group
    """
    # Base query: exclude already processed items
    base_query = db.query(Article).options(joinedload(Article.source)).filter(
        Article.is_bookmarked == False,
        Article.is_dismissed == False,
        Article.is_archived == False
    )

    # Get remaining count for UI
    remaining_count = base_query.count()

    # Split into high-score and discovery
    high_score_count = int(limit * 0.7)
    discovery_count = limit - high_score_count

    # High score items (score >= 50)
    high_score_items = base_query.filter(
        Article.score >= 50
    ).order_by(func.random()).limit(high_score_count).all()

    # Discovery items (score < 50 or null)
    discovery_items = base_query.filter(
        (Article.score < 50) | (Article.score.is_(None))
    ).order_by(func.random()).limit(discovery_count).all()

    # Combine and shuffle
    all_items = high_score_items + discovery_items
    random.shuffle(all_items)

    # Transform to response
    items_data = []
    for item in all_items:
        item_dict = {
            **item.__dict__,
            'source_type': item.source.type if item.source else None
        }
        items_data.append(ArticleResponse.model_validate(item_dict))

    logger.info(f"Retrieved {len(items_data)} triage items (remaining: {remaining_count})")

    return TriageResponse(
        items=items_data,
        remaining_count=remaining_count
    )


@router.post("/articles/{article_id}/dismiss")
async def dismiss_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Mark an article as dismissed (won't appear in triage)"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.is_dismissed = True
    db.commit()

    logger.info(f"Article {article_id} dismissed from triage")

    return {"success": True, "message": "Article dismissed"}
```

**Step 2: Verify syntax**

Run:
```bash
cd backend && poetry run python -c "from app.api.triage import router; print('OK')"
```
Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/api/triage.py
git commit -m "feat(api): add triage endpoints"
```

---

### Task 6: Register Routers in Main

**Files:**
- Modify: `backend/app/main.py:1-14` and `38-49`

**Step 1: Add imports**

After line 13 (`from app.api.admin import router as admin_router`), add:

```python
from app.api.library import router as library_router
from app.api.triage import router as triage_router
```

**Step 2: Register routers**

After line 49 (`app.include_router(admin_router, prefix="/api", tags=["admin"])`), add:

```python
app.include_router(library_router, prefix="/api", tags=["library"])
app.include_router(triage_router, prefix="/api", tags=["triage"])
```

**Step 3: Verify app starts**

Run:
```bash
cd backend && timeout 5 poetry run uvicorn app.main:app --port 8001 || true
```
Expected: App starts without import errors

**Step 4: Commit**

```bash
git add backend/app/main.py
git commit -m "feat(api): register library and triage routers"
```

---

### Task 7: Test Backend Endpoints

**Step 1: Start backend server**

Run in background:
```bash
cd backend && poetry run uvicorn app.main:app --port 8001 &
sleep 3
```

**Step 2: Test library endpoint**

Run:
```bash
curl -s http://localhost:8001/api/library | jq '.total'
```
Expected: A number (likely 0)

**Step 3: Test triage endpoint**

Run:
```bash
curl -s http://localhost:8001/api/triage | jq '.remaining_count'
```
Expected: A number

**Step 4: Test bookmark toggle**

Run:
```bash
# Get first article ID
ARTICLE_ID=$(curl -s "http://localhost:8001/api/articles?limit=1" | jq '.data[0].id')
# Toggle bookmark
curl -s -X POST "http://localhost:8001/api/articles/${ARTICLE_ID}/bookmark" | jq '.is_bookmarked'
```
Expected: `true`

**Step 5: Stop server and commit**

```bash
pkill -f "uvicorn app.main:app --port 8001" || true
git add -A
git commit -m "test: verify library and triage endpoints work"
```

---

## Phase 3: Frontend Types & API Client

### Task 8: Update Frontend Types

**Files:**
- Modify: `frontend/types/index.ts:3-28`

**Step 1: Add new fields to Article interface**

After line 23 (`is_archived: boolean;`), add:

```typescript
  is_bookmarked: boolean;
  is_dismissed: boolean;
  bookmarked_at?: string;
```

**Step 2: Add LibraryItem and TriageResponse types**

At end of file, add:

```typescript

export interface LibraryResponse {
  items: Article[];
  total: number;
  unread_count: number;
}

export interface TriageResponse {
  items: Article[];
  remaining_count: number;
}

export type LibraryFilter = 'all' | 'article' | 'video';
export type LibraryView = 'list' | 'grid';
```

**Step 3: Commit**

```bash
git add frontend/types/index.ts
git commit -m "feat(types): add library and triage types"
```

---

### Task 9: Update API Client

**Files:**
- Modify: `frontend/lib/api-client.ts`

**Step 1: Add import for new types**

Update line 2 to include new types:

```typescript
import type { Article, Video, Keyword, Source, UserConfig, ArticleFilters, PaginatedResponse, LibraryResponse, TriageResponse, LibraryFilter } from '@/types';
```

**Step 2: Add libraryApi after articlesApi (around line 144)**

After `articlesApi` object, add:

```typescript

// Library API
export const libraryApi = {
  getLibrary: async (params?: { type?: LibraryFilter; unread_only?: boolean; limit?: number; offset?: number }): Promise<LibraryResponse> => {
    const response = await apiClient.get('/library', { params });
    return {
      ...response.data,
      items: response.data.items.map((item: any) => ({
        ...item,
        id: String(item.id),
        tags: item.tags || [],
      })),
    };
  },

  toggleBookmark: async (id: string): Promise<Article> => {
    const response = await apiClient.post(`/articles/${id}/bookmark`);
    return {
      ...response.data,
      id: String(response.data.id),
      tags: response.data.tags || [],
    };
  },
};

// Triage API
export const triageApi = {
  getTriageItems: async (limit: number = 10): Promise<TriageResponse> => {
    const response = await apiClient.get('/triage', { params: { limit } });
    return {
      ...response.data,
      items: response.data.items.map((item: any) => ({
        ...item,
        id: String(item.id),
        tags: item.tags || [],
      })),
    };
  },

  dismissArticle: async (id: string): Promise<{ success: boolean }> => {
    const response = await apiClient.post(`/articles/${id}/dismiss`);
    return response.data;
  },
};
```

**Step 3: Commit**

```bash
git add frontend/lib/api-client.ts
git commit -m "feat(api-client): add library and triage API methods"
```

---

## Phase 4: Frontend Hooks

### Task 10: Create useLibrary Hook

**Files:**
- Create: `frontend/hooks/use-library.ts`

**Step 1: Write the hook**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { libraryApi } from '@/lib/api-client';
import { toast } from '@/hooks/use-toast';
import type { Article, LibraryFilter } from '@/types';

export const useLibrary = (params?: { type?: LibraryFilter; unread_only?: boolean }) => {
  return useQuery({
    queryKey: ['library', params],
    queryFn: () => libraryApi.getLibrary(params),
    staleTime: 30 * 1000, // 30 seconds
  });
};

export const useToggleBookmark = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => libraryApi.toggleBookmark(articleId),

    onMutate: async (articleId) => {
      // Cancel outgoing queries
      await queryClient.cancelQueries({ queryKey: ['library'] });
      await queryClient.cancelQueries({ queryKey: ['articles'] });

      // Snapshot previous values
      const previousLibrary = queryClient.getQueryData(['library']);
      const previousArticles = queryClient.getQueryData(['articles']);

      return { previousLibrary, previousArticles };
    },

    onError: (_err, _variables, context) => {
      // Rollback on error
      if (context?.previousLibrary) {
        queryClient.setQueryData(['library'], context.previousLibrary);
      }
      if (context?.previousArticles) {
        queryClient.setQueryData(['articles'], context.previousArticles);
      }
      toast({
        title: "Erreur",
        description: "Impossible de mettre a jour la bibliotheque",
        variant: "destructive",
      });
    },

    onSuccess: (data) => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['library'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });

      toast({
        title: data.is_bookmarked ? "Ajoute a la bibliotheque" : "Retire de la bibliotheque",
        description: data.is_bookmarked
          ? "L'article a ete ajoute a votre bibliotheque"
          : "L'article a ete retire de votre bibliotheque",
      });
    },
  });
};
```

**Step 2: Commit**

```bash
git add frontend/hooks/use-library.ts
git commit -m "feat(hooks): add useLibrary and useToggleBookmark"
```

---

### Task 11: Create useTriage Hook

**Files:**
- Create: `frontend/hooks/use-triage.ts`

**Step 1: Write the hook**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { triageApi, libraryApi } from '@/lib/api-client';
import { toast } from '@/hooks/use-toast';

export const useTriage = (limit: number = 10) => {
  return useQuery({
    queryKey: ['triage', limit],
    queryFn: () => triageApi.getTriageItems(limit),
    staleTime: 60 * 1000, // 1 minute
  });
};

export const useDismissArticle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => triageApi.dismissArticle(articleId),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['triage'] });
    },

    onError: () => {
      toast({
        title: "Erreur",
        description: "Impossible de rejeter l'article",
        variant: "destructive",
      });
    },
  });
};

export const useTriageBookmark = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => libraryApi.toggleBookmark(articleId),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['triage'] });
      queryClient.invalidateQueries({ queryKey: ['library'] });

      toast({
        title: "Ajoute a la bibliotheque",
        description: "L'article a ete sauvegarde",
      });
    },

    onError: () => {
      toast({
        title: "Erreur",
        description: "Impossible de sauvegarder l'article",
        variant: "destructive",
      });
    },
  });
};
```

**Step 2: Commit**

```bash
git add frontend/hooks/use-triage.ts
git commit -m "feat(hooks): add useTriage, useDismissArticle, useTriageBookmark"
```

---

## Phase 5: Update Existing Components

### Task 12: Wire Bookmark Button in ArticleCard

**Files:**
- Modify: `frontend/components/feed/ArticleCard.tsx:14,30,172-178`

**Step 1: Add import for useToggleBookmark**

After line 14 (`import { useToggleFavorite } from "@/hooks/use-toggle-favorite";`), add:

```typescript
import { useToggleBookmark } from "@/hooks/use-library";
```

**Step 2: Add hook usage**

After line 30 (`const toggleFavorite = useToggleFavorite();`), add:

```typescript
  const toggleBookmark = useToggleBookmark();
```

**Step 3: Wire up the button**

Replace lines 172-178 (the BookmarkPlus button) with:

```typescript
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleBookmark.mutate(localArticle.id)}
              className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
            >
              <BookmarkPlus
                className={cn(
                  "w-4 h-4",
                  localArticle.is_bookmarked && "fill-violet-400 text-violet-400"
                )}
              />
            </Button>
```

**Step 4: Commit**

```bash
git add frontend/components/feed/ArticleCard.tsx
git commit -m "feat(ArticleCard): wire bookmark button to useToggleBookmark"
```

---

### Task 13: Update Sidebar Navigation

**Files:**
- Modify: `frontend/components/layout/Sidebar.tsx:8,11-16`

**Step 1: Add icon imports**

Update line 8 to add Bookmark and Shuffle icons:

```typescript
import { Home, Settings, BarChart3, ChevronLeft, FileText, Bookmark, Shuffle } from 'lucide-react';
```

**Step 2: Add nav items**

Replace lines 11-16 (navItems array) with:

```typescript
const navItems = [
  { href: '/', icon: Home, label: 'Feed' },
  { href: '/articles', icon: FileText, label: 'Articles' },
  { href: '/library', icon: Bookmark, label: 'Library' },
  { href: '/triage', icon: Shuffle, label: 'Triage' },
  { href: '/config', icon: Settings, label: 'Configuration' },
  { href: '/analytics', icon: BarChart3, label: 'Analytics' },
];
```

**Step 3: Commit**

```bash
git add frontend/components/layout/Sidebar.tsx
git commit -m "feat(Sidebar): add Library and Triage navigation items"
```

---

## Phase 6: Library Page Components

### Task 14: Create LibraryCard Component

**Files:**
- Create: `frontend/components/library/LibraryCard.tsx`

**Step 1: Write the component**

```typescript
"use client";

import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExternalLink, X, Play, FileText } from "lucide-react";
import { formatRelativeDate } from "@/lib/date-utils";
import { cn } from "@/lib/utils";
import type { Article } from "@/types";

interface LibraryCardProps {
  item: Article;
  onRemove: (id: string) => void;
  onOpen: (item: Article) => void;
}

export const LibraryCard = ({ item, onRemove, onOpen }: LibraryCardProps) => {
  const isVideo = item.is_video || item.video_id;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className={cn(
        "relative group p-4 bg-anthracite-800/80 border border-violet-500/30 rounded-lg",
        "hover:bg-anthracite-700/80 hover:border-violet-400/50 transition-all duration-300",
        item.is_read && "opacity-60"
      )}
    >
      {/* Unread indicator */}
      {!item.is_read && (
        <div className="absolute top-2 left-2 w-2 h-2 bg-violet-400 rounded-full" />
      )}

      {/* Remove button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onRemove(item.id)}
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity text-violet-300/70 hover:text-red-400 hover:bg-red-500/20"
      >
        <X className="w-4 h-4" />
      </Button>

      {/* Thumbnail for videos */}
      {isVideo && item.thumbnail_url && (
        <div
          className="relative mb-3 rounded-md overflow-hidden cursor-pointer"
          onClick={() => onOpen(item)}
        >
          <img
            src={item.thumbnail_url}
            alt={item.title}
            className="w-full h-32 object-cover"
          />
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
            <Play className="w-10 h-10 text-white" />
          </div>
        </div>
      )}

      {/* Content */}
      <div className="cursor-pointer" onClick={() => onOpen(item)}>
        {/* Type icon + Title */}
        <div className="flex items-start gap-2 mb-2">
          {isVideo ? (
            <Play className="w-4 h-4 text-violet-400 mt-1 shrink-0" />
          ) : (
            <FileText className="w-4 h-4 text-violet-400 mt-1 shrink-0" />
          )}
          <h3 className="font-semibold text-violet-100 line-clamp-2 hover:text-violet-300 transition-colors">
            {item.title}
          </h3>
        </div>

        {/* Meta */}
        <div className="flex items-center gap-2 text-xs text-violet-300/60 mb-2">
          <span className="capitalize">{item.source_type}</span>
          <span>-</span>
          <span>{formatRelativeDate(item.bookmarked_at || item.created_at)}</span>
          {item.score && (
            <>
              <span>-</span>
              <span className="text-violet-400">{item.score.toFixed(0)} pts</span>
            </>
          )}
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1">
          <Badge variant="secondary" className="text-xs bg-violet-500/20 text-violet-200">
            {item.category}
          </Badge>
        </div>
      </div>

      {/* External link */}
      <Button
        variant="ghost"
        size="sm"
        asChild
        className="absolute bottom-2 right-2 text-violet-300/70 hover:text-violet-200"
      >
        <a href={item.url} target="_blank" rel="noopener noreferrer">
          <ExternalLink className="w-4 h-4" />
        </a>
      </Button>
    </motion.div>
  );
};
```

**Step 2: Commit**

```bash
mkdir -p frontend/components/library
git add frontend/components/library/LibraryCard.tsx
git commit -m "feat(LibraryCard): create grid card component"
```

---

### Task 15: Create LibraryItem Component (List View)

**Files:**
- Create: `frontend/components/library/LibraryItem.tsx`

**Step 1: Write the component**

```typescript
"use client";

import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExternalLink, X, Play, FileText } from "lucide-react";
import { formatRelativeDate } from "@/lib/date-utils";
import { cn } from "@/lib/utils";
import type { Article } from "@/types";

interface LibraryItemProps {
  item: Article;
  onRemove: (id: string) => void;
  onOpen: (item: Article) => void;
}

export const LibraryItem = ({ item, onRemove, onOpen }: LibraryItemProps) => {
  const isVideo = item.is_video || item.video_id;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className={cn(
        "flex items-center gap-4 p-3 bg-anthracite-800/80 border border-violet-500/30 rounded-lg",
        "hover:bg-anthracite-700/80 hover:border-violet-400/50 transition-all duration-300",
        item.is_read && "opacity-60"
      )}
    >
      {/* Unread indicator */}
      <div className={cn(
        "w-2 h-2 rounded-full shrink-0",
        item.is_read ? "bg-transparent" : "bg-violet-400"
      )} />

      {/* Type icon */}
      {isVideo ? (
        <Play className="w-5 h-5 text-violet-400 shrink-0" />
      ) : (
        <FileText className="w-5 h-5 text-violet-400 shrink-0" />
      )}

      {/* Content */}
      <div
        className="flex-1 min-w-0 cursor-pointer"
        onClick={() => onOpen(item)}
      >
        <h3 className="font-medium text-violet-100 truncate hover:text-violet-300 transition-colors">
          {item.title}
        </h3>
        <div className="flex items-center gap-2 text-xs text-violet-300/60">
          <span className="capitalize">{item.source_type}</span>
          <span>-</span>
          <span>{formatRelativeDate(item.bookmarked_at || item.created_at)}</span>
        </div>
      </div>

      {/* Score */}
      {item.score && (
        <Badge variant="secondary" className="shrink-0 bg-violet-500/20 text-violet-200">
          {item.score.toFixed(0)}
        </Badge>
      )}

      {/* Actions */}
      <div className="flex items-center gap-1 shrink-0">
        <Button
          variant="ghost"
          size="sm"
          asChild
          className="text-violet-300/70 hover:text-violet-200"
        >
          <a href={item.url} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="w-4 h-4" />
          </a>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onRemove(item.id)}
          className="text-violet-300/70 hover:text-red-400 hover:bg-red-500/20"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>
    </motion.div>
  );
};
```

**Step 2: Commit**

```bash
git add frontend/components/library/LibraryItem.tsx
git commit -m "feat(LibraryItem): create list row component"
```

---

### Task 16: Create LibraryFilters Component

**Files:**
- Create: `frontend/components/library/LibraryFilters.tsx`

**Step 1: Write the component**

```typescript
"use client";

import { Button } from "@/components/ui/button";
import { LayoutGrid, List, FileText, Play, Eye } from "lucide-react";
import { cn } from "@/lib/utils";
import type { LibraryFilter, LibraryView } from "@/types";

interface LibraryFiltersProps {
  view: LibraryView;
  onViewChange: (view: LibraryView) => void;
  filter: LibraryFilter;
  onFilterChange: (filter: LibraryFilter) => void;
  unreadOnly: boolean;
  onUnreadOnlyChange: (value: boolean) => void;
  total: number;
  unreadCount: number;
}

export const LibraryFilters = ({
  view,
  onViewChange,
  filter,
  onFilterChange,
  unreadOnly,
  onUnreadOnlyChange,
  total,
  unreadCount,
}: LibraryFiltersProps) => {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      {/* Filter buttons */}
      <div className="flex items-center gap-2">
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          size="sm"
          onClick={() => onFilterChange('all')}
          className={cn(
            filter === 'all'
              ? 'bg-violet-600 text-white'
              : 'border-violet-500/30 text-violet-300'
          )}
        >
          All ({total})
        </Button>
        <Button
          variant={filter === 'article' ? 'default' : 'outline'}
          size="sm"
          onClick={() => onFilterChange('article')}
          className={cn(
            filter === 'article'
              ? 'bg-violet-600 text-white'
              : 'border-violet-500/30 text-violet-300'
          )}
        >
          <FileText className="w-4 h-4 mr-1" />
          Articles
        </Button>
        <Button
          variant={filter === 'video' ? 'default' : 'outline'}
          size="sm"
          onClick={() => onFilterChange('video')}
          className={cn(
            filter === 'video'
              ? 'bg-violet-600 text-white'
              : 'border-violet-500/30 text-violet-300'
          )}
        >
          <Play className="w-4 h-4 mr-1" />
          Videos
        </Button>
        <Button
          variant={unreadOnly ? 'default' : 'outline'}
          size="sm"
          onClick={() => onUnreadOnlyChange(!unreadOnly)}
          className={cn(
            unreadOnly
              ? 'bg-violet-600 text-white'
              : 'border-violet-500/30 text-violet-300'
          )}
        >
          <Eye className="w-4 h-4 mr-1" />
          Unread ({unreadCount})
        </Button>
      </div>

      {/* View toggle */}
      <div className="flex items-center gap-1 border border-violet-500/30 rounded-lg p-1">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onViewChange('list')}
          className={cn(
            "px-2",
            view === 'list'
              ? 'bg-violet-500/20 text-violet-200'
              : 'text-violet-300/70'
          )}
        >
          <List className="w-4 h-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onViewChange('grid')}
          className={cn(
            "px-2",
            view === 'grid'
              ? 'bg-violet-500/20 text-violet-200'
              : 'text-violet-300/70'
          )}
        >
          <LayoutGrid className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add frontend/components/library/LibraryFilters.tsx
git commit -m "feat(LibraryFilters): create filter bar component"
```

---

### Task 17: Create Library Page

**Files:**
- Create: `frontend/app/library/page.tsx`

**Step 1: Write the page**

```typescript
"use client";

import { useState, useEffect } from "react";
import { AnimatePresence } from "framer-motion";
import { Bookmark } from "lucide-react";
import { useLibrary, useToggleBookmark } from "@/hooks/use-library";
import { LibraryCard } from "@/components/library/LibraryCard";
import { LibraryItem } from "@/components/library/LibraryItem";
import { LibraryFilters } from "@/components/library/LibraryFilters";
import { articlesApi } from "@/lib/api-client";
import type { Article, LibraryFilter, LibraryView } from "@/types";

export default function LibraryPage() {
  // Persist view preference
  const [view, setView] = useState<LibraryView>('grid');
  const [filter, setFilter] = useState<LibraryFilter>('all');
  const [unreadOnly, setUnreadOnly] = useState(false);

  // Load view preference from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('library-view');
    if (saved === 'list' || saved === 'grid') {
      setView(saved);
    }
  }, []);

  // Save view preference
  const handleViewChange = (newView: LibraryView) => {
    setView(newView);
    localStorage.setItem('library-view', newView);
  };

  const { data, isLoading, error } = useLibrary({
    type: filter === 'all' ? undefined : filter,
    unread_only: unreadOnly,
  });

  const toggleBookmark = useToggleBookmark();

  const handleRemove = (id: string) => {
    toggleBookmark.mutate(id);
  };

  const handleOpen = async (item: Article) => {
    // Mark as read
    if (!item.is_read) {
      await articlesApi.markRead(item.id);
    }
    // Open in new tab
    window.open(item.url, '_blank');
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-anthracite-700 rounded w-48" />
          <div className="h-10 bg-anthracite-700 rounded w-full" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-48 bg-anthracite-700 rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-red-400">Error loading library</div>
      </div>
    );
  }

  const items = data?.items || [];
  const total = data?.total || 0;
  const unreadCount = data?.unread_count || 0;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Bookmark className="w-8 h-8 text-violet-400" />
        <div>
          <h1 className="text-2xl font-bold text-violet-100">Library</h1>
          <p className="text-sm text-violet-300/60">{total} items saved</p>
        </div>
      </div>

      {/* Filters */}
      <LibraryFilters
        view={view}
        onViewChange={handleViewChange}
        filter={filter}
        onFilterChange={setFilter}
        unreadOnly={unreadOnly}
        onUnreadOnlyChange={setUnreadOnly}
        total={total}
        unreadCount={unreadCount}
      />

      {/* Content */}
      {items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Bookmark className="w-16 h-16 text-violet-500/30 mb-4" />
          <h2 className="text-xl font-semibold text-violet-200 mb-2">
            Your library is empty
          </h2>
          <p className="text-violet-300/60 max-w-md">
            Add items from the Feed by clicking the bookmark icon, or try Triage mode to discover new content.
          </p>
        </div>
      ) : view === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <AnimatePresence mode="popLayout">
            {items.map((item) => (
              <LibraryCard
                key={item.id}
                item={item}
                onRemove={handleRemove}
                onOpen={handleOpen}
              />
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <div className="space-y-2">
          <AnimatePresence mode="popLayout">
            {items.map((item) => (
              <LibraryItem
                key={item.id}
                item={item}
                onRemove={handleRemove}
                onOpen={handleOpen}
              />
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
```

**Step 2: Commit**

```bash
mkdir -p frontend/app/library
git add frontend/app/library/page.tsx
git commit -m "feat(library): create Library page with grid/list views"
```

---

## Phase 7: Triage Page Components

### Task 18: Create TriageCard Component

**Files:**
- Create: `frontend/components/triage/TriageCard.tsx`

**Step 1: Write the component**

```typescript
"use client";

import { motion, useMotionValue, useTransform, PanInfo } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Play, FileText, ChevronDown } from "lucide-react";
import { formatRelativeDate } from "@/lib/date-utils";
import { cn } from "@/lib/utils";
import type { Article } from "@/types";

interface TriageCardProps {
  item: Article;
  onSwipeLeft: () => void;
  onSwipeRight: () => void;
  onTap: () => void;
}

export const TriageCard = ({ item, onSwipeLeft, onSwipeRight, onTap }: TriageCardProps) => {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-15, 15]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0.5, 1, 1, 1, 0.5]);

  // Color indicators for swipe direction
  const leftIndicatorOpacity = useTransform(x, [-150, -50, 0], [1, 0.5, 0]);
  const rightIndicatorOpacity = useTransform(x, [0, 50, 150], [0, 0.5, 1]);

  const isVideo = item.is_video || item.video_id;

  const handleDragEnd = (_: any, info: PanInfo) => {
    const threshold = 100;
    if (info.offset.x > threshold) {
      onSwipeRight();
    } else if (info.offset.x < -threshold) {
      onSwipeLeft();
    }
  };

  return (
    <div className="relative w-full max-w-md mx-auto">
      {/* Swipe indicators */}
      <motion.div
        className="absolute -left-16 top-1/2 -translate-y-1/2 text-red-400 font-bold text-lg"
        style={{ opacity: leftIndicatorOpacity }}
      >
        SKIP
      </motion.div>
      <motion.div
        className="absolute -right-16 top-1/2 -translate-y-1/2 text-green-400 font-bold text-lg"
        style={{ opacity: rightIndicatorOpacity }}
      >
        SAVE
      </motion.div>

      {/* Card */}
      <motion.div
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={0.9}
        onDragEnd={handleDragEnd}
        style={{ x, rotate, opacity }}
        whileTap={{ cursor: "grabbing" }}
        className={cn(
          "relative p-6 bg-anthracite-800 border-2 border-violet-500/40 rounded-2xl shadow-xl",
          "cursor-grab active:cursor-grabbing"
        )}
      >
        {/* Thumbnail for videos */}
        {isVideo && item.thumbnail_url && (
          <div className="relative mb-4 rounded-lg overflow-hidden">
            <img
              src={item.thumbnail_url}
              alt={item.title}
              className="w-full h-48 object-cover"
            />
            <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
              <Play className="w-14 h-14 text-white" />
            </div>
          </div>
        )}

        {/* Type badge */}
        <div className="flex items-center gap-2 mb-3">
          {isVideo ? (
            <Badge className="bg-red-500/20 text-red-300 border-red-500/30">
              <Play className="w-3 h-3 mr-1" />
              Video
            </Badge>
          ) : (
            <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30">
              <FileText className="w-3 h-3 mr-1" />
              Article
            </Badge>
          )}
          <Badge variant="secondary" className="bg-violet-500/20 text-violet-200">
            {item.category}
          </Badge>
        </div>

        {/* Title */}
        <h2 className="text-xl font-bold text-violet-100 mb-3 line-clamp-3">
          {item.title}
        </h2>

        {/* Meta */}
        <div className="flex items-center gap-2 text-sm text-violet-300/60 mb-4">
          <span className="capitalize">{item.source_type}</span>
          <span>-</span>
          <span>{formatRelativeDate(item.published_at)}</span>
          {item.read_time_minutes && (
            <>
              <span>-</span>
              <span>{item.read_time_minutes} min read</span>
            </>
          )}
        </div>

        {/* Score */}
        {item.score && (
          <div className="flex items-center gap-2 mb-4">
            <span className="text-violet-300/60 text-sm">Relevance:</span>
            <div className="flex-1 h-2 bg-anthracite-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-violet-600 to-violet-400"
                style={{ width: `${Math.min(item.score, 100)}%` }}
              />
            </div>
            <span className="text-violet-200 font-semibold">{item.score.toFixed(0)}</span>
          </div>
        )}

        {/* Summary preview */}
        {item.summary && (
          <p className="text-violet-200/70 text-sm line-clamp-3 mb-4">
            {item.summary}
          </p>
        )}

        {/* Tap for more */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onTap();
          }}
          className="flex items-center justify-center gap-2 w-full py-2 text-violet-400 hover:text-violet-300 transition-colors"
        >
          <span className="text-sm">Tap for more details</span>
          <ChevronDown className="w-4 h-4" />
        </button>

        {/* Swipe hints */}
        <div className="flex justify-between mt-4 pt-4 border-t border-violet-500/20 text-xs text-violet-300/50">
          <span>← Swipe left to skip</span>
          <span>Swipe right to save →</span>
        </div>
      </motion.div>
    </div>
  );
};
```

**Step 2: Commit**

```bash
mkdir -p frontend/components/triage
git add frontend/components/triage/TriageCard.tsx
git commit -m "feat(TriageCard): create swipeable card component"
```

---

### Task 19: Create TriageModal Component

**Files:**
- Create: `frontend/components/triage/TriageModal.tsx`

**Step 1: Write the component**

```typescript
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X, ExternalLink, BookmarkPlus, Ban, Play, FileText } from "lucide-react";
import { formatRelativeDate } from "@/lib/date-utils";
import type { Article } from "@/types";

interface TriageModalProps {
  item: Article | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
  onSkip: () => void;
}

export const TriageModal = ({ item, isOpen, onClose, onSave, onSkip }: TriageModalProps) => {
  if (!item) return null;

  const isVideo = item.is_video || item.video_id;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            className="fixed inset-x-4 bottom-4 top-20 md:inset-x-auto md:left-1/2 md:-translate-x-1/2 md:w-full md:max-w-2xl z-50 bg-anthracite-900 border border-violet-500/40 rounded-2xl overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-violet-500/20">
              <div className="flex items-center gap-2">
                {isVideo ? (
                  <Badge className="bg-red-500/20 text-red-300 border-red-500/30">
                    <Play className="w-3 h-3 mr-1" />
                    Video
                  </Badge>
                ) : (
                  <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30">
                    <FileText className="w-3 h-3 mr-1" />
                    Article
                  </Badge>
                )}
                <span className="text-violet-300/60 text-sm capitalize">{item.source_type}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {/* Thumbnail */}
              {isVideo && item.thumbnail_url && (
                <div className="relative mb-4 rounded-lg overflow-hidden">
                  <img
                    src={item.thumbnail_url}
                    alt={item.title}
                    className="w-full h-64 object-cover"
                  />
                </div>
              )}

              {/* Title */}
              <h2 className="text-2xl font-bold text-violet-100 mb-4">
                {item.title}
              </h2>

              {/* Meta */}
              <div className="flex flex-wrap items-center gap-3 text-sm text-violet-300/60 mb-4">
                {item.author && <span>By {item.author}</span>}
                <span>{formatRelativeDate(item.published_at)}</span>
                {item.read_time_minutes && <span>{item.read_time_minutes} min read</span>}
                {item.score && (
                  <Badge variant="secondary" className="bg-violet-500/20 text-violet-200">
                    Score: {item.score.toFixed(0)}
                  </Badge>
                )}
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-6">
                <Badge variant="secondary" className="bg-violet-500/20 text-violet-200">
                  {item.category}
                </Badge>
                {item.tags?.slice(0, 5).map((tag) => (
                  <Badge key={tag} variant="outline" className="border-violet-500/30 text-violet-300/70">
                    {tag}
                  </Badge>
                ))}
              </div>

              {/* Summary */}
              {item.summary && (
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-violet-300 mb-2">Summary</h3>
                  <p className="text-violet-200/80 leading-relaxed">
                    {item.summary}
                  </p>
                </div>
              )}

              {/* Content preview */}
              {item.content && (
                <div>
                  <h3 className="text-sm font-semibold text-violet-300 mb-2">Preview</h3>
                  <p className="text-violet-200/70 leading-relaxed line-clamp-10">
                    {item.content}
                  </p>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3 p-4 border-t border-violet-500/20 bg-anthracite-800">
              <Button
                variant="outline"
                className="flex-1 border-red-500/30 text-red-300 hover:bg-red-500/20"
                onClick={() => {
                  onSkip();
                  onClose();
                }}
              >
                <Ban className="w-4 h-4 mr-2" />
                Skip
              </Button>
              <Button
                variant="outline"
                className="flex-1 border-green-500/30 text-green-300 hover:bg-green-500/20"
                onClick={() => {
                  onSave();
                  onClose();
                }}
              >
                <BookmarkPlus className="w-4 h-4 mr-2" />
                Save to Library
              </Button>
              <Button
                variant="ghost"
                asChild
                className="text-violet-300 hover:text-violet-200"
              >
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4" />
                </a>
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
```

**Step 2: Commit**

```bash
git add frontend/components/triage/TriageModal.tsx
git commit -m "feat(TriageModal): create detail modal component"
```

---

### Task 20: Create Triage Page

**Files:**
- Create: `frontend/app/triage/page.tsx`

**Step 1: Write the page**

```typescript
"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shuffle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTriage, useDismissArticle, useTriageBookmark } from "@/hooks/use-triage";
import { TriageCard } from "@/components/triage/TriageCard";
import { TriageModal } from "@/components/triage/TriageModal";
import Link from "next/link";
import type { Article } from "@/types";

export default function TriagePage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [modalItem, setModalItem] = useState<Article | null>(null);
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null);

  const { data, isLoading, error, refetch } = useTriage(10);
  const dismissArticle = useDismissArticle();
  const bookmarkArticle = useTriageBookmark();

  const items = data?.items || [];
  const remainingCount = data?.remaining_count || 0;
  const currentItem = items[currentIndex];

  const goToNext = useCallback(() => {
    if (currentIndex < items.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      // Refetch when we've gone through all items
      setCurrentIndex(0);
      refetch();
    }
  }, [currentIndex, items.length, refetch]);

  const handleSwipeLeft = useCallback(() => {
    if (!currentItem) return;
    setExitDirection('left');
    dismissArticle.mutate(currentItem.id, {
      onSettled: () => {
        setTimeout(() => {
          setExitDirection(null);
          goToNext();
        }, 300);
      },
    });
  }, [currentItem, dismissArticle, goToNext]);

  const handleSwipeRight = useCallback(() => {
    if (!currentItem) return;
    setExitDirection('right');
    bookmarkArticle.mutate(currentItem.id, {
      onSettled: () => {
        setTimeout(() => {
          setExitDirection(null);
          goToNext();
        }, 300);
      },
    });
  }, [currentItem, bookmarkArticle, goToNext]);

  const handleTap = useCallback(() => {
    if (currentItem) {
      setModalItem(currentItem);
    }
  }, [currentItem]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="animate-spin w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] text-center p-6">
        <div className="text-red-400 mb-4">Error loading triage items</div>
        <Button onClick={() => refetch()}>Try Again</Button>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] text-center p-6">
        <Shuffle className="w-16 h-16 text-violet-500/30 mb-4" />
        <h2 className="text-xl font-semibold text-violet-200 mb-2">
          All caught up!
        </h2>
        <p className="text-violet-300/60 max-w-md mb-6">
          You've triaged all available content. Check back later for new articles and videos.
        </p>
        <Link href="/">
          <Button variant="outline" className="border-violet-500/30 text-violet-300">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Feed
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] flex flex-col p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Shuffle className="w-8 h-8 text-violet-400" />
          <div>
            <h1 className="text-2xl font-bold text-violet-100">Triage</h1>
            <p className="text-sm text-violet-300/60">
              {remainingCount} items remaining
            </p>
          </div>
        </div>
        <Link href="/">
          <Button variant="ghost" className="text-violet-300/70">
            Exit
          </Button>
        </Link>
      </div>

      {/* Card stack */}
      <div className="flex-1 flex items-center justify-center">
        <AnimatePresence mode="wait">
          {currentItem && !exitDirection && (
            <motion.div
              key={currentItem.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{
                opacity: 0,
                x: exitDirection === 'left' ? -300 : exitDirection === 'right' ? 300 : 0,
                rotate: exitDirection === 'left' ? -20 : exitDirection === 'right' ? 20 : 0,
              }}
              transition={{ duration: 0.3 }}
            >
              <TriageCard
                item={currentItem}
                onSwipeLeft={handleSwipeLeft}
                onSwipeRight={handleSwipeRight}
                onTap={handleTap}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Progress indicator */}
      <div className="flex justify-center gap-1 mt-6">
        {items.slice(0, 10).map((_, i) => (
          <div
            key={i}
            className={`w-2 h-2 rounded-full transition-colors ${
              i === currentIndex ? 'bg-violet-400' : i < currentIndex ? 'bg-violet-600' : 'bg-violet-800'
            }`}
          />
        ))}
      </div>

      {/* Modal */}
      <TriageModal
        item={modalItem}
        isOpen={!!modalItem}
        onClose={() => setModalItem(null)}
        onSave={handleSwipeRight}
        onSkip={handleSwipeLeft}
      />
    </div>
  );
}
```

**Step 2: Commit**

```bash
mkdir -p frontend/app/triage
git add frontend/app/triage/page.tsx
git commit -m "feat(triage): create Triage page with swipe interface"
```

---

## Phase 8: Final Verification

### Task 21: Build and Test Frontend

**Step 1: Install any missing dependencies**

Run:
```bash
cd frontend && npm install
```

**Step 2: Type check**

Run:
```bash
cd frontend && npx tsc --noEmit
```
Expected: No type errors

**Step 3: Lint check**

Run:
```bash
cd frontend && npm run lint
```
Expected: No lint errors (or only warnings)

**Step 4: Build**

Run:
```bash
cd frontend && npm run build
```
Expected: Build succeeds

**Step 5: Commit final verification**

```bash
git add -A
git commit -m "chore: verify build passes for library and triage features"
```

---

### Task 22: Create Feature Branch Merge Commit

**Step 1: Ensure all changes are committed**

Run:
```bash
git status
```
Expected: Working tree clean

**Step 2: Log all commits for this feature**

Run:
```bash
git log --oneline -20
```

**Step 3: Create summary commit if needed**

If there are uncommitted changes:
```bash
git add -A
git commit -m "feat: complete library and triage feature implementation"
```

---

## Summary

This plan implements:

1. **Database**: 3 new fields (`is_bookmarked`, `is_dismissed`, `bookmarked_at`) with indexes
2. **Backend**: 2 new routers (`library.py`, `triage.py`) with 4 endpoints
3. **Frontend Types**: Updated `Article` interface, new `LibraryResponse` and `TriageResponse`
4. **Frontend Hooks**: `useLibrary`, `useToggleBookmark`, `useTriage`, `useDismissArticle`, `useTriageBookmark`
5. **Frontend Components**:
   - Library: `LibraryCard`, `LibraryItem`, `LibraryFilters`
   - Triage: `TriageCard`, `TriageModal`
6. **Frontend Pages**: `/library` and `/triage`
7. **Sidebar**: Updated navigation with Library and Triage links
8. **ArticleCard**: Wired bookmark button

Total: 22 tasks with ~25 commits
