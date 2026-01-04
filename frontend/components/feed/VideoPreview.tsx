'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, Play, Star } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatRelativeDate } from '@/lib/date-utils';
import type { Video } from '@/types';
import { LikeDislikeButtons } from './LikeDislikeButtons';

interface VideoPreviewProps {
  video: Video;
  onToggleFavorite?: (id: string) => void;
  compact?: boolean;
}

// Extract YouTube video ID from various URL formats
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

// Get thumbnail URL based on platform
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

  // Fallback placeholder
  return '/placeholder-video.png';
};

export const VideoPreview = ({ video, onToggleFavorite, compact = false }: VideoPreviewProps) => {
  const thumbnailUrl = getThumbnailUrl(video);
  const scoreColor = video.score >= 70 ? 'text-gold' : video.score >= 50 ? 'text-gold-light' : 'text-muted-foreground';

  if (compact) {
    return (
      <div className="group border border-gold/30 bg-black/50 hover:bg-black/70 hover:border-gold/50 transition-all">
        {/* Thumbnail */}
        <div className="relative aspect-video bg-black/50 overflow-hidden">
          <img
            src={thumbnailUrl}
            alt={video.title}
            className="w-full h-full object-cover transition-transform group-hover:scale-105"
            onError={(e) => {
              e.currentTarget.src = '/placeholder-video.png';
            }}
          />
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <Play className="w-12 h-12 text-white" />
          </div>
          {video.duration_minutes && (
            <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-0.5 text-xs text-white rounded">
              {video.duration_minutes}min
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-3">
          <div className="flex items-start justify-between gap-2 mb-2">
            <h4 className="text-sm font-semibold leading-tight line-clamp-2 flex-1">
              {video.title}
            </h4>
            <div className={cn('text-lg font-bold shrink-0', scoreColor)}>
              {video.score.toFixed(0)}
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
            <span className="capitalize">{video.source_type}</span>
            <span>•</span>
            <span>{formatRelativeDate(video.published_at)}</span>
          </div>

          <div className="flex items-center justify-between">
            <LikeDislikeButtons
              initialLikes={video.likes}
              initialDislikes={video.dislikes}
              userReaction={video.user_reaction}
              size="sm"
              showCounts={false}
            />

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onToggleFavorite?.(video.id)}
              >
                <Star
                  className={cn(
                    'w-3 h-3',
                    video.is_favorite && 'fill-gold text-gold-light'
                  )}
                />
              </Button>
              <Button variant="ghost" size="sm" asChild>
                <a
                  href={video.video_url || video.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="w-3 h-3" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Full size preview
  return (
    <div className="group border border-gold/30 bg-black/50 hover:bg-black/70 hover:border-gold/50 transition-all rounded-lg overflow-hidden">
      {/* Thumbnail */}
      <div className="relative aspect-video bg-black/50 overflow-hidden">
        <img
          src={thumbnailUrl}
          alt={video.title}
          className="w-full h-full object-cover transition-transform group-hover:scale-105"
          onError={(e) => {
            e.currentTarget.src = '/placeholder-video.png';
          }}
        />
        <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <Play className="w-16 h-16 text-white" />
        </div>
        {video.duration_minutes && (
          <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 text-sm text-white rounded">
            {video.duration_minutes}min
          </div>
        )}
        <div className="absolute top-2 right-2">
          <Badge variant="default" className={cn('font-bold', scoreColor)}>
            {video.score.toFixed(0)}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-bold text-lg leading-tight mb-2 line-clamp-2">
          {video.title}
        </h3>

        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
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
        <div className="flex flex-wrap gap-1.5 mb-3">
          <Badge variant="secondary" className="text-xs">
            {video.category}
          </Badge>
          {(video.tags || []).slice(0, 2).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>

        {/* Summary */}
        {video.summary && (
          <p className="text-sm text-muted-foreground leading-relaxed mb-3 line-clamp-2">
            {video.summary}
          </p>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between border-t pt-3">
          <LikeDislikeButtons
            initialLikes={video.likes}
            initialDislikes={video.dislikes}
            userReaction={video.user_reaction}
          />

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onToggleFavorite?.(video.id)}
            >
              <Star
                className={cn(
                  'w-4 h-4',
                  video.is_favorite && 'fill-gold text-gold-light'
                )}
              />
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <a
                href={video.video_url || video.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
