'use client';

import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, X, Play, Circle, ThumbsUp, ThumbsDown, FileText } from 'lucide-react';
import { formatRelativeDate } from '@/lib/date-utils';
import { cn } from '@/lib/utils';
import type { Article } from '@/types';

interface LibraryCardProps {
  article: Article;
  onRemove: (id: string) => void;
  onOpen: (article: Article) => void;
  onLike?: (id: string) => void;
  onDislike?: (id: string) => void;
}

export const LibraryCard = ({ article, onRemove, onOpen, onLike, onDislike }: LibraryCardProps) => {
  const isVideo = article.source_type === 'youtube' || article.source_type === 'youtube_rss' || article.source_type === 'youtube_trending' || article.source_type === 'video';
  const isLiked = article.user_reaction === 'like' || article.is_liked;
  const isDisliked = article.user_reaction === 'dislike' || article.is_disliked;

  // Get preview text from summary or content
  const previewText = article.summary || article.content;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={cn(
        'group relative flex flex-col h-full bg-anthracite-800/80 border border-violet-500/30 rounded-lg overflow-hidden',
        'hover:border-violet-400/50 transition-all duration-300',
        !article.is_read && 'ring-2 ring-violet-500/30'
      )}
    >
      {/* Thumbnail for videos */}
      {isVideo && article.thumbnail_url ? (
        <div
          className="relative aspect-video cursor-pointer group/thumb shrink-0"
          onClick={() => onOpen(article)}
        >
          <img
            src={article.thumbnail_url}
            alt={article.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover/thumb:opacity-100 transition-opacity">
            <div className="w-12 h-12 rounded-full bg-violet-600/90 flex items-center justify-center">
              <Play className="w-6 h-6 text-white fill-white ml-1" />
            </div>
          </div>
          {/* Unread indicator on thumbnail */}
          {!article.is_read && (
            <div className="absolute top-2 left-2">
              <Circle className="w-3 h-3 fill-violet-400 text-violet-400" />
            </div>
          )}
        </div>
      ) : (
        /* Article preview image placeholder */
        <div
          className="relative h-24 bg-gradient-to-br from-violet-900/30 to-anthracite-900 flex items-center justify-center cursor-pointer shrink-0"
          onClick={() => onOpen(article)}
        >
          <FileText className="w-10 h-10 text-violet-500/40" />
          {/* Unread indicator */}
          {!article.is_read && (
            <div className="absolute top-2 left-2">
              <Circle className="w-3 h-3 fill-violet-400 text-violet-400" />
            </div>
          )}
        </div>
      )}

      {/* Content - grows to fill space */}
      <div className="flex-1 p-4 flex flex-col">
        <h3
          className="font-semibold text-violet-100 mb-2 line-clamp-2 cursor-pointer hover:text-violet-300 transition-colors"
          onClick={() => onOpen(article)}
        >
          {article.title}
        </h3>

        <div className="flex items-center gap-2 text-xs text-violet-300/60 mb-2">
          <span className="capitalize">{article.source_type}</span>
          <span>-</span>
          <span>{formatRelativeDate(article.bookmarked_at || article.created_at)}</span>
        </div>

        {/* Preview text for articles */}
        {!isVideo && previewText && (
          <p className="text-xs text-violet-300/50 line-clamp-2 mb-2 flex-1">
            {previewText}
          </p>
        )}

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-2">
          <Badge
            variant="secondary"
            className="text-xs bg-violet-500/20 text-violet-200 border-violet-400/30"
          >
            {article.category}
          </Badge>
        </div>

        {/* Score - pushed to bottom of content area */}
        <div className="flex items-center justify-between mt-auto">
          <div className="flex items-center gap-1">
            <span className={cn(
              'text-lg font-bold',
              article.score >= 70 ? 'text-violet-400' : 'text-violet-300/70'
            )}>
              {article.score?.toFixed(0) || 'N/A'}
            </span>
            <span className="text-xs text-violet-300/50">score</span>
          </div>

          {article.read_time_minutes && (
            <span className="text-xs text-violet-300/50">
              {article.read_time_minutes} min
            </span>
          )}
        </div>
      </div>

      {/* Actions - always at bottom */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-violet-500/20 bg-anthracite-900/50 shrink-0">
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onLike?.(article.id)}
            className={cn(
              "text-violet-300/70 hover:text-green-400 hover:bg-green-500/20",
              isLiked && "text-green-400 bg-green-500/20"
            )}
          >
            <ThumbsUp className={cn("w-4 h-4", isLiked && "fill-current")} />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDislike?.(article.id)}
            className={cn(
              "text-violet-300/70 hover:text-red-400 hover:bg-red-500/20",
              isDisliked && "text-red-400 bg-red-500/20"
            )}
          >
            <ThumbsDown className={cn("w-4 h-4", isDisliked && "fill-current")} />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onRemove(article.id)}
            className="text-violet-300/70 hover:text-red-400 hover:bg-red-500/20"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <Button
          variant="ghost"
          size="sm"
          asChild
          className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
        >
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="w-4 h-4 mr-1" />
            Open
          </a>
        </Button>
      </div>
    </motion.div>
  );
};
