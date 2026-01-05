'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Play, Trophy, Star, ExternalLink } from 'lucide-react';
import { CornerBrackets } from '@/components/cyberpunk';
import { LikeDislikeButtons } from '@/components/feed/LikeDislikeButtons';
import { Skeleton } from '@/components/ui/skeleton';
import { formatRelativeDate } from '@/lib/date-utils';
import { videosApi } from '@/lib/api-client';
import { cn } from '@/lib/utils';
import type { Video } from '@/types';

// Extract YouTube video ID
const getYouTubeVideoId = (url: string): string | null => {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
    /^([a-zA-Z0-9_-]{11})$/
  ];

  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }

  return null;
};

// Get thumbnail URL
const getThumbnailUrl = (video: Video): string => {
  if (video.thumbnail_url) {
    return video.thumbnail_url;
  }

  if (video.platform === 'youtube') {
    const videoId = video.video_id || getYouTubeVideoId(video.video_url || video.url);
    if (videoId) {
      return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
    }
  }

  return '/placeholder-video.png';
};

export const BestVideoCard = () => {
  const [video, setVideo] = useState<Video | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBestVideo = async () => {
      try {
        setIsLoading(true);
        const bestVideo = await videosApi.getBestOfWeek();
        setVideo(bestVideo);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch best video:', err);
        setError('Failed to load video');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBestVideo();
  }, []);

  const handleToggleFavorite = async () => {
    if (!video) return;
    try {
      const updated = await videosApi.toggleFavorite(video.id);
      setVideo(updated);
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const handleLike = async () => {
    if (!video) return;
    try {
      const updated = await videosApi.toggleLike(video.id);
      setVideo(updated);
    } catch (err) {
      console.error('Failed to like video:', err);
    }
  };

  const handleDislike = async () => {
    if (!video) return;
    try {
      const updated = await videosApi.toggleDislike(video.id);
      setVideo(updated);
    } catch (err) {
      console.error('Failed to dislike video:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="w-full">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="w-6 h-6 text-gold-light" />
          <h2 className="text-2xl font-bold">Video of the Week</h2>
        </div>
        <CornerBrackets color="gold">
          <div className="bg-charcoal-900/50 border border-gold/30 p-6 space-y-4">
            <Skeleton className="w-full aspect-video" />
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </CornerBrackets>
      </div>
    );
  }

  if (error || !video) {
    return (
      <div className="w-full">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="w-6 h-6 text-gold-light" />
          <h2 className="text-2xl font-bold">Video of the Week</h2>
        </div>
        <CornerBrackets color="gold">
          <div className="bg-black/50 border border-gold/30 p-6">
            <p className="text-center text-muted-foreground">
              {error || 'No videos available'}
            </p>
          </div>
        </CornerBrackets>
      </div>
    );
  }

  const thumbnailUrl = getThumbnailUrl(video);
  const scoreColor = (video.score ?? 0) >= 70 ? 'text-gold' : (video.score ?? 0) >= 50 ? 'text-gold-light' : 'text-muted-foreground';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="w-full"
    >
      <div className="flex items-center gap-2 mb-4">
        <Trophy className="w-6 h-6 text-gold-light animate-pulse" />
        <h2 className="text-2xl font-bold glow-text">Video of the Week</h2>
      </div>

      <CornerBrackets color="gold">
        <div className="bg-charcoal-900/50 border border-gold/30 backdrop-blur-sm hover:bg-charcoal-800/70 hover:border-gold/50 transition-all overflow-hidden">
          {/* Video Thumbnail */}
          <div className="relative aspect-video bg-charcoal-900/50 group cursor-pointer">
            <img
              src={thumbnailUrl}
              alt={video.title}
              className="w-full h-full object-cover transition-transform group-hover:scale-105"
              onError={(e) => {
                e.currentTarget.src = '/placeholder-video.png';
              }}
            />
            <div className="absolute inset-0 bg-charcoal-950/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <Play className="w-20 h-20 text-white drop-shadow-lg" />
            </div>
            {video.duration_minutes && (
              <div className="absolute bottom-4 right-4 bg-charcoal-950/80 px-3 py-1 text-sm text-white rounded">
                {video.duration_minutes}min
              </div>
            )}
            <div className="absolute top-4 right-4">
              <Badge variant="default" className={cn('font-bold text-lg px-3 py-1', scoreColor)}>
                {video.score?.toFixed(0) ?? '-'}
              </Badge>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            <h3 className="text-2xl font-bold leading-tight mb-2 glow-text">
              {video.title}
            </h3>

            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
              <span className="capitalize">{video.source_type}</span>
              <span>•</span>
              <span>{formatRelativeDate(video.published_at)}</span>
              {video.views && (
                <>
                  <span>•</span>
                  <span>{video.views.toLocaleString()} views</span>
                </>
              )}
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-4">
              <Badge variant="default" className="text-sm">
                {video.category}
              </Badge>
              {(video.tags || []).slice(0, 4).map((tag) => (
                <Badge key={tag} variant="outline" className="text-sm">
                  {tag}
                </Badge>
              ))}
            </div>

            {/* Summary */}
            {video.summary && (
              <p className="text-base text-muted-foreground leading-relaxed mb-4">
                {video.summary}
              </p>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between border-t border-gold/20 pt-4">
              <LikeDislikeButtons
                initialLikes={video.likes}
                initialDislikes={video.dislikes}
                userReaction={video.user_reaction}
                onLike={handleLike}
                onDislike={handleDislike}
                size="md"
              />

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="default"
                  onClick={handleToggleFavorite}
                >
                  <Star
                    className={cn(
                      'w-5 h-5',
                      video.is_favorite && 'fill-gold text-gold-light'
                    )}
                  />
                </Button>
                <Button variant="default" asChild>
                  <a
                    href={video.video_url || video.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="gap-2"
                  >
                    Watch Video
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </CornerBrackets>
    </motion.div>
  );
};
