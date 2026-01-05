'use client';

import { ParallaxGrid } from '@/components/home/ParallaxGrid';
import { Hero3D } from '@/components/home/Hero3D';
import { BestArticleCard3D } from '@/components/home/BestArticleCard3D';
import { BestVideoCard3D } from '@/components/home/BestVideoCard3D';
import { StatsPreview3D } from '@/components/home/StatsPreview3D';
import { useState, useEffect } from 'react';
import { articlesApi, videosApi } from '@/lib/api-client';
import type { Article, Video } from '@/types';

export default function HomePage() {
  // Fetch best article (uses engagement-based scoring from API)
  const [bestArticle, setBestArticle] = useState<Article | null>(null);
  const [bestVideo, setBestVideo] = useState<Video | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchBestContent = async () => {
      try {
        const [article, video] = await Promise.all([
          articlesApi.getBestOfWeek(),
          videosApi.getBestOfWeek(),
        ]);
        setBestArticle(article);
        setBestVideo(video);
      } catch (err) {
        console.error('Failed to fetch best content:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchBestContent();
  }, []);

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
