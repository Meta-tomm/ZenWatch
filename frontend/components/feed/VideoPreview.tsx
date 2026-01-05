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
  onLike?: (id: string) => void;
  onDislike?: (id: string) => void;
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

export const VideoPreview = ({ video, onToggleFavorite, onLike, onDislike, compact = false }: VideoPreviewProps) => {
  const thumbnailUrl = getThumbnailUrl(video);
  const scoreColor = (video.score ?? 0) >= 70 ? 'text-violet-400' : (video.score ?? 0) >= 50 ? 'text-violet-300' : 'text-violet-300/60';

  if (compact) {
    return (
      <div className="group border border-violet-500/30 bg-gradient-to-br from-anthracite-800/60 to-anthracite-900/60 hover:from-anthracite-700/60 hover:to-anthracite-800/60 hover:border-violet-400/50 transition-all rounded-lg overflow-hidden">
        {/* Thumbnail */}
        <div className="relative aspect-video bg-anthracite-900/50 overflow-hidden">
          <img
            src={thumbnailUrl}
            alt={video.title}
            className="w-full h-full object-cover transition-transform group-hover:scale-105"
            onError={(e) => {
              e.currentTarget.src = '/placeholder-video.png';
            }}
          />
          <div className="absolute inset-0 bg-violet-950/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <Play className="w-12 h-12 text-violet-200" />
          </div>
          {video.duration_minutes && (
            <div className="absolute bottom-2 right-2 bg-violet-950/90 px-2 py-0.5 text-xs text-violet-200 rounded border border-violet-500/30">
              {video.duration_minutes}min
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-3">
          <div className="flex items-start justify-between gap-2 mb-2">
            <h4 className="text-sm font-semibold leading-tight line-clamp-2 flex-1 text-violet-100">
              {video.title}
            </h4>
            <div className={cn('text-lg font-bold shrink-0', scoreColor)}>
              {video.score?.toFixed(0) ?? '-'}
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-violet-300/60 mb-2">
            <span className="capitalize">{video.source_type}</span>
            <span>•</span>
            <span>{formatRelativeDate(video.published_at)}</span>
          </div>

          <div className="flex items-center justify-between">
            <LikeDislikeButtons
              initialLikes={video.likes}
              initialDislikes={video.dislikes}
              userReaction={video.user_reaction}
              onLike={() => onLike?.(video.id)}
              onDislike={() => onDislike?.(video.id)}
              size="sm"
              showCounts={false}
            />

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onToggleFavorite?.(video.id)}
                className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
              >
                <Star
                  className={cn(
                    'w-3 h-3',
                    video.is_favorite && 'fill-violet-400 text-violet-400'
                  )}
                />
              </Button>
              <Button variant="ghost" size="sm" asChild className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20">
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
    <div className="group border border-violet-500/30 bg-gradient-to-br from-anthracite-800/60 to-anthracite-900/60 hover:from-anthracite-700/60 hover:to-anthracite-800/60 hover:border-violet-400/50 transition-all rounded-lg overflow-hidden">
      {/* Thumbnail */}
      <div className="relative aspect-video bg-anthracite-900/50 overflow-hidden">
        <img
          src={thumbnailUrl}
          alt={video.title}
          className="w-full h-full object-cover transition-transform group-hover:scale-105"
          onError={(e) => {
            e.currentTarget.src = '/placeholder-video.png';
          }}
        />
        <div className="absolute inset-0 bg-violet-950/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <Play className="w-16 h-16 text-violet-200" />
        </div>
        {video.duration_minutes && (
          <div className="absolute bottom-2 right-2 bg-violet-950/90 px-2 py-1 text-sm text-violet-200 rounded border border-violet-500/30">
            {video.duration_minutes}min
          </div>
        )}
        <div className="absolute top-2 right-2">
          <Badge className={cn('font-bold bg-violet-500/30 border-violet-400/50', scoreColor)}>
            {video.score?.toFixed(0) ?? '-'}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-bold text-lg leading-tight mb-2 line-clamp-2 text-violet-100">
          {video.title}
        </h3>

        <div className="flex items-center gap-2 text-sm text-violet-300/60 mb-3">
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
          <Badge className="text-xs bg-violet-500/20 text-violet-200 border-violet-400/30">
            {video.category}
          </Badge>
          {(video.tags || []).slice(0, 2).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs border-violet-500/30 text-violet-300/70">
              {tag}
            </Badge>
          ))}
        </div>

        {/* Summary */}
        {video.summary && (
          <p className="text-sm text-violet-200/70 leading-relaxed mb-3 line-clamp-2">
            {video.summary}
          </p>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between border-t border-violet-500/20 pt-3">
          <LikeDislikeButtons
            initialLikes={video.likes}
            initialDislikes={video.dislikes}
            userReaction={video.user_reaction}
            onLike={() => onLike?.(video.id)}
            onDislike={() => onDislike?.(video.id)}
          />

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onToggleFavorite?.(video.id)}
              className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
            >
              <Star
                className={cn(
                  'w-4 h-4',
                  video.is_favorite && 'fill-violet-400 text-violet-400'
                )}
              />
            </Button>
            <Button variant="ghost" size="sm" asChild className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20">
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
