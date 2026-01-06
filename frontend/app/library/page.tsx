'use client';

import { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Bookmark } from 'lucide-react';
import { useLibrary, useRemoveFromLibrary } from '@/hooks/use-library';
import { LibraryCard } from '@/components/library/LibraryCard';
import { LibraryItem } from '@/components/library/LibraryItem';
import { LibraryFilters } from '@/components/library/LibraryFilters';
import { Skeleton } from '@/components/ui/skeleton';
import { articlesApi } from '@/lib/api-client';
import type { Article, LibraryFilter, LibraryView } from '@/types';

export default function LibraryPage() {
  const [filter, setFilter] = useState<LibraryFilter>('all');
  const [view, setView] = useState<LibraryView>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('libraryView') as LibraryView) || 'grid';
    }
    return 'grid';
  });
  const [unreadOnly, setUnreadOnly] = useState(false);

  const { data, isLoading, error } = useLibrary({
    type: filter === 'all' ? undefined : filter,
    unread_only: unreadOnly,
  });

  const removeFromLibrary = useRemoveFromLibrary();

  // Persist view preference
  useEffect(() => {
    localStorage.setItem('libraryView', view);
  }, [view]);

  const handleRemove = (id: string) => {
    removeFromLibrary.mutate(id);
  };

  const handleOpen = async (article: Article) => {
    // Mark as read when opening
    if (!article.is_read) {
      try {
        await articlesApi.markRead(article.id);
      } catch (err) {
        console.error('Failed to mark article as read:', err);
      }
    }
    window.open(article.url, '_blank');
  };

  if (error) {
    return (
      <main className="min-h-screen bg-anthracite-950">
        <div className="container max-w-6xl py-8">
          <div className="flex items-center justify-center h-64">
            <p className="text-red-400">Failed to load library</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-anthracite-950">
      <div className="container max-w-6xl py-8 space-y-6">
        {/* Header */}
        <div className="p-6 rounded-2xl bg-anthracite-800/50 border border-violet-500/20">
          <div className="flex items-center gap-3 mb-2">
            <Bookmark className="w-8 h-8 text-violet-400" />
            <h1 className="text-3xl font-bold text-gradient-violet">
              Library
            </h1>
          </div>
          {data && (
            <p className="text-violet-300/60 ml-11">
              {data.total} items saved
              {data.unread_count > 0 && ` - ${data.unread_count} unread`}
            </p>
          )}
        </div>

        {/* Filters */}
        <div className="p-4 rounded-xl bg-anthracite-800/50 border border-violet-500/20">
          <LibraryFilters
            filter={filter}
            view={view}
            unreadOnly={unreadOnly}
            onFilterChange={setFilter}
            onViewChange={setView}
            onUnreadOnlyChange={setUnreadOnly}
          />
        </div>

        {/* Content */}
        {isLoading ? (
          <div className={view === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-2'}>
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton
                key={i}
                className={view === 'grid' ? 'h-48 bg-anthracite-800/50' : 'h-20 bg-anthracite-800/50'}
              />
            ))}
          </div>
        ) : data?.items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center rounded-2xl bg-anthracite-800/50 border border-violet-500/20">
            <Bookmark className="w-16 h-16 text-violet-500/30 mb-4" />
            <h2 className="text-xl font-semibold text-violet-200 mb-2">
              Your library is empty
            </h2>
            <p className="text-violet-300/60 max-w-md">
              Add items from the Feed or try Triage mode to discover new content.
            </p>
          </div>
        ) : view === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <AnimatePresence>
              {data?.items.map((article) => (
                <LibraryCard
                  key={article.id}
                  article={article}
                  onRemove={handleRemove}
                  onOpen={handleOpen}
                />
              ))}
            </AnimatePresence>
          </div>
        ) : (
          <div className="space-y-2">
            <AnimatePresence>
              {data?.items.map((article) => (
                <LibraryItem
                  key={article.id}
                  article={article}
                  onRemove={handleRemove}
                  onOpen={handleOpen}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </main>
  );
}
