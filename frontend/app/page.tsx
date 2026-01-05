'use client';

import { ParallaxGrid } from '@/components/home/ParallaxGrid';
import { Hero3D } from '@/components/home/Hero3D';
import { BestArticleCard3D } from '@/components/home/BestArticleCard3D';
import { BestVideoCard3D } from '@/components/home/BestVideoCard3D';
import { StatsPreview3D } from '@/components/home/StatsPreview3D';
import { useArticles } from '@/hooks/use-articles';
import { useMemo } from 'react';

export default function HomePage() {
  // Fetch all articles
  const { data: articlesResponse, isLoading } = useArticles({
    sort: 'score',
  });

  // Flatten pages from infinite query
  const articles = useMemo(() => {
    return articlesResponse?.pages?.flatMap(page => page.data) || [];
  }, [articlesResponse]);

  // Find best article of the week (highest score, not video)
  const bestArticle = useMemo(() => {
    return articles
      .filter(a => !a.source_type?.startsWith('youtube'))
      .sort((a, b) => (b.score ?? 0) - (a.score ?? 0))[0] || null;
  }, [articles]);

  // Find best video of the week (highest score, YouTube only)
  const bestVideo = useMemo(() => {
    return articles
      .filter(a => a.source_type?.startsWith('youtube'))
      .sort((a, b) => (b.score ?? 0) - (a.score ?? 0))[0] || null;
  }, [articles]);

  return (
    <main className="relative min-h-screen bg-anthracite-950 overflow-hidden">
      {/* Parallax background */}
      <ParallaxGrid />

      {/* Content */}
      <div className="relative z-10">
        {/* Hero section */}
        <Hero3D />

        {/* Best content cards */}
        <section className="max-w-7xl mx-auto px-4 py-16">
          {isLoading ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="h-96 rounded-2xl bg-anthracite-800/50 animate-pulse" />
              <div className="h-96 rounded-2xl bg-anthracite-800/50 animate-pulse" />
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <BestArticleCard3D article={bestArticle} />
              <BestVideoCard3D video={bestVideo} />
            </div>
          )}
        </section>

        {/* Stats section */}
        <StatsPreview3D />
      </div>
    </main>
  );
}
