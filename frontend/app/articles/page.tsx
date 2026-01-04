'use client';

import { FilterBar } from '@/components/feed/FilterBar';
import { ArticleFeed } from '@/components/feed/ArticleFeed';
import { ArticleModal } from '@/components/feed/ArticleModal';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function ArticlesPage() {
  return (
    <main className="min-h-screen bg-cyber-black">
      {/* Header with back button */}
      <div className="sticky top-0 z-40 border-b border-cyber-green/20 bg-cyber-black/95 backdrop-blur supports-[backdrop-filter]:bg-cyber-black/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="sm" className="gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Back to Home
                </Button>
              </Link>
              <h1 className="text-2xl font-bold text-cyber-green">
                Tech Feed
              </h1>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <FilterBar />

      {/* Article Feed */}
      <div className="container mx-auto">
        <ArticleFeed />
      </div>

      {/* Article Modal */}
      <ArticleModal />
    </main>
  );
}
