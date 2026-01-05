'use client';

import { useEffect, useState } from 'react';
import { VideoPreview } from './VideoPreview';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Video as VideoIcon, AlertCircle } from 'lucide-react';
import { videosApi } from '@/lib/api-client';
import { useUIStore } from '@/store/ui-store';
import type { Video } from '@/types';

export const VideoPanel = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { videoFilters, setVideoFilters, activeFilters } = useUIStore();

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        setIsLoading(true);
        const response = await videosApi.getVideos({
          sort: videoFilters.sort,
          timeRange: activeFilters.timeRange,
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
  }, [videoFilters.sort, activeFilters.timeRange]);

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
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <VideoIcon className="w-5 h-5 text-violet-400" />
            <h2 className="font-bold text-lg text-gradient-violet">Videos</h2>
            {!isLoading && (
              <span className="text-xs text-violet-400/70">({videos.length})</span>
            )}
          </div>
          <Select
            value={videoFilters.sort}
            onValueChange={(value) =>
              setVideoFilters({ sort: value as 'score' | 'date' | 'popularity' })
            }
          >
            <SelectTrigger className="w-24 h-8 text-xs bg-anthracite-800/70 border-violet-500/30 text-violet-100 focus:border-violet-400 focus:ring-violet-400/30">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-anthracite-900/95 border-violet-500/30">
              <SelectItem value="score" className="text-xs text-violet-100 hover:bg-violet-500/20 focus:bg-violet-500/20">Score</SelectItem>
              <SelectItem value="date" className="text-xs text-violet-100 hover:bg-violet-500/20 focus:bg-violet-500/20">Date</SelectItem>
              <SelectItem value="popularity" className="text-xs text-violet-100 hover:bg-violet-500/20 focus:bg-violet-500/20">Views</SelectItem>
            </SelectContent>
          </Select>
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
