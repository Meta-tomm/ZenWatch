'use client';

import { useState, useCallback } from 'react';
import { Shuffle, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useTriage, useDismissArticle, useTriageBookmark } from '@/hooks/use-triage';
import { TriageCard } from '@/components/triage/TriageCard';
import { TriageModal } from '@/components/triage/TriageModal';
import Link from 'next/link';
import type { Article } from '@/types';

export default function TriagePage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data, isLoading, error, refetch } = useTriage(10);
  const dismissArticle = useDismissArticle();
  const bookmarkArticle = useTriageBookmark();

  const currentArticle = data?.items[currentIndex];

  const handleSwipeLeft = useCallback(() => {
    if (currentArticle) {
      dismissArticle.mutate(currentArticle.id);
    }
    // Move to next card or refetch if at end
    if (data && currentIndex >= data.items.length - 2) {
      refetch();
      setCurrentIndex(0);
    } else {
      setCurrentIndex((prev) => prev + 1);
    }
  }, [currentArticle, currentIndex, data, dismissArticle, refetch]);

  const handleSwipeRight = useCallback(() => {
    if (currentArticle) {
      bookmarkArticle.mutate(currentArticle.id);
    }
    // Move to next card or refetch if at end
    if (data && currentIndex >= data.items.length - 2) {
      refetch();
      setCurrentIndex(0);
    } else {
      setCurrentIndex((prev) => prev + 1);
    }
  }, [currentArticle, currentIndex, data, bookmarkArticle, refetch]);

  const handleTap = useCallback(() => {
    if (currentArticle) {
      setSelectedArticle(currentArticle);
      setIsModalOpen(true);
    }
  }, [currentArticle]);

  const handleModalDismiss = useCallback(() => {
    if (selectedArticle) {
      dismissArticle.mutate(selectedArticle.id);
    }
    if (data && currentIndex >= data.items.length - 2) {
      refetch();
      setCurrentIndex(0);
    } else {
      setCurrentIndex((prev) => prev + 1);
    }
  }, [selectedArticle, currentIndex, data, dismissArticle, refetch]);

  const handleModalBookmark = useCallback(() => {
    if (selectedArticle) {
      bookmarkArticle.mutate(selectedArticle.id);
    }
    if (data && currentIndex >= data.items.length - 2) {
      refetch();
      setCurrentIndex(0);
    } else {
      setCurrentIndex((prev) => prev + 1);
    }
  }, [selectedArticle, currentIndex, data, bookmarkArticle, refetch]);

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">Failed to load triage items</p>
          <Button onClick={() => refetch()}>Try again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col p-6 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-violet-100 flex items-center gap-2">
            <Shuffle className="w-6 h-6" />
            Triage
          </h1>
          <p className="text-sm text-violet-300/60 mt-1">
            Discover new content
            {data && data.remaining_count > 0 && (
              <span> - {data.remaining_count} items remaining</span>
            )}
          </p>
        </div>

        <Button
          variant="ghost"
          asChild
          className="text-violet-300/70 hover:text-violet-200"
        >
          <Link href="/">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Exit
          </Link>
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center">
        {isLoading ? (
          <div className="w-full max-w-md">
            <Skeleton className="h-96 bg-anthracite-800 rounded-xl" />
          </div>
        ) : !currentArticle || data?.items.length === 0 ? (
          <div className="text-center">
            <Shuffle className="w-16 h-16 text-violet-500/30 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-violet-200 mb-2">
              All caught up!
            </h2>
            <p className="text-violet-300/60 max-w-md mb-6">
              No new items to triage. Check back later or explore the Feed.
            </p>
            <div className="flex items-center justify-center gap-4">
              <Button asChild variant="outline">
                <Link href="/">Go to Feed</Link>
              </Button>
              <Button asChild>
                <Link href="/library">View Library</Link>
              </Button>
            </div>
          </div>
        ) : (
          <TriageCard
            key={currentArticle.id}
            article={currentArticle}
            onSwipeLeft={handleSwipeLeft}
            onSwipeRight={handleSwipeRight}
            onTap={handleTap}
          />
        )}
      </div>

      {/* Modal */}
      <TriageModal
        article={selectedArticle}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onDismiss={handleModalDismiss}
        onBookmark={handleModalBookmark}
      />
    </div>
  );
}
