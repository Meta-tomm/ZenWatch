'use client';

import { useEffect, useState } from 'react';
import { VideoPreview } from './VideoPreview';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Video as VideoIcon, AlertCircle } from 'lucide-react';
import { videosApi } from '@/lib/api-client';
import type { Video } from '@/types';

export const VideoPanel = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        setIsLoading(true);
        const response = await videosApi.getVideos({
          sort: 'score',
          limit: 50,
        });
        setVideos(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch videos:', err);
        setError('Failed to load videos');
      } finally {
        setIsLoading(false);
      }
    };

    fetchVideos();
  }, []);

  const handleToggleFavorite = async (id: string) => {
    try {
      const updated = await videosApi.toggleFavorite(id);
      setVideos(videos.map(v => v.id === id ? updated : v));
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  if (error) {
    return (
      <div className="h-full bg-gradient-to-b from-anthracite-800/50 to-anthracite-900/50 backdrop-blur-sm border-l border-violet-500/20 p-4">
        <div className="flex items-center gap-2 mb-4">
          <VideoIcon className="w-5 h-5 text-violet-400" />
          <h2 className="font-bold text-lg text-gradient-violet">Videos</h2>
        </div>
        <div className="flex flex-col items-center justify-center h-32 text-violet-300/70">
          <AlertCircle className="w-8 h-8 mb-2 text-violet-400/50" />
          <p className="text-sm text-violet-300/60">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gradient-to-b from-anthracite-800/50 to-anthracite-900/50 backdrop-blur-sm border-l border-violet-500/20">
      <div className="p-4 border-b border-violet-500/20 sticky top-0 bg-anthracite-900/90 backdrop-blur z-10">
        <div className="flex items-center gap-2">
          <VideoIcon className="w-5 h-5 text-violet-400" />
          <h2 className="font-bold text-lg text-gradient-violet">Top Videos</h2>
          {!isLoading && (
            <span className="text-xs text-violet-400/70">({videos.length})</span>
          )}
        </div>
      </div>

      <ScrollArea className="h-[calc(100vh-8rem)]">
        <div className="p-4 space-y-4">
          {isLoading ? (
            // Loading skeletons
            Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="w-full aspect-video" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            ))
          ) : videos.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32">
              <VideoIcon className="w-8 h-8 mb-2 text-violet-400/40" />
              <p className="text-sm text-violet-300/60">No videos available</p>
            </div>
          ) : (
            videos.map((video) => (
              <VideoPreview
                key={video.id}
                video={video}
                onToggleFavorite={handleToggleFavorite}
                compact
              />
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
};
