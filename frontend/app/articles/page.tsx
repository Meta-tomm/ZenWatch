'use client';

import { FilterBar } from '@/components/feed/FilterBar';
import { ArticleFeed } from '@/components/feed/ArticleFeed';
import { VideoPanel } from '@/components/feed/VideoPanel';
import { ArticleModal } from '@/components/feed/ArticleModal';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function ArticlesPage() {
  return (
    <main className="min-h-screen bg-charcoal-950">
      {/* Header with back button */}
      <div className="sticky top-0 z-40 border-b border-gold-dark/20 bg-charcoal-900/95 backdrop-blur supports-[backdrop-filter]:bg-charcoal-900/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="sm" className="gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Back to Home
                </Button>
              </Link>
              <h1 className="text-2xl font-bold text-gold-dark">
                Research Hub
              </h1>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <FilterBar />

      {/* Two-column layout: Articles + Videos */}
      <div className="flex h-[calc(100vh-12rem)]">
        {/* Articles Feed (Main area) */}
        <div className="flex-1 overflow-hidden">
          <ArticleFeed />
        </div>

        {/* Video Panel (Side panel) - blends seamlessly */}
        <div className="w-80 xl:w-96 hidden md:block overflow-hidden">
          <VideoPanel />
        </div>
      </div>

      {/* Article Modal */}
      <ArticleModal />
    </main>
  );
}
