'use client';

import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, X, Play, Circle } from 'lucide-react';
import { formatRelativeDate } from '@/lib/date-utils';
import { cn } from '@/lib/utils';
import type { Article } from '@/types';

interface LibraryItemProps {
  article: Article;
  onRemove: (id: string) => void;
  onOpen: (article: Article) => void;
}

export const LibraryItem = ({ article, onRemove, onOpen }: LibraryItemProps) => {
  const isVideo = article.source_type === 'youtube' || article.source_type === 'youtube_rss' || article.source_type === 'video';

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -10 }}
      className={cn(
        'group flex items-center gap-4 p-3 bg-anthracite-800/80 border border-violet-500/30 rounded-lg',
        'hover:bg-anthracite-700/80 hover:border-violet-400/50 transition-all duration-300'
      )}
    >
      {/* Thumbnail or unread indicator */}
      {isVideo && article.thumbnail_url ? (
        <div
          className="shrink-0 relative w-24 h-14 rounded overflow-hidden cursor-pointer group/thumb"
          onClick={() => onOpen(article)}
        >
          <img
            src={article.thumbnail_url}
            alt={article.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover/thumb:opacity-100 transition-opacity">
            <Play className="w-6 h-6 text-white fill-white" />
          </div>
          {!article.is_read && (
            <div className="absolute top-1 left-1">
              <Circle className="w-2 h-2 fill-violet-400 text-violet-400" />
            </div>
          )}
        </div>
      ) : (
        <div className="shrink-0 w-3">
          {!article.is_read && (
            <Circle className="w-3 h-3 fill-violet-400 text-violet-400" />
          )}
        </div>
      )}

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h3
            className="font-semibold text-violet-100 truncate cursor-pointer hover:text-violet-300 transition-colors"
            onClick={() => onOpen(article)}
          >
            {article.title}
          </h3>
        </div>

        <div className="flex items-center gap-3 text-xs text-violet-300/60">
          <span className="capitalize">{article.source_type}</span>
          <span>-</span>
          <Badge
            variant="secondary"
            className="text-xs bg-violet-500/20 text-violet-200 border-violet-400/30"
          >
            {article.category}
          </Badge>
          <span>-</span>
          <span>{formatRelativeDate(article.bookmarked_at || article.created_at)}</span>
          {article.read_time_minutes && (
            <>
              <span>-</span>
              <span>{article.read_time_minutes} min</span>
            </>
          )}
        </div>
      </div>

      {/* Score */}
      <div className="shrink-0 text-center">
        <div className={cn(
          'text-xl font-bold',
          article.score >= 70 ? 'text-violet-400' : 'text-violet-300/70'
        )}>
          {article.score?.toFixed(0) || 'N/A'}
        </div>
      </div>

      {/* Actions */}
      <div className="shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onRemove(article.id)}
          className="text-violet-300/70 hover:text-red-400 hover:bg-red-500/20"
        >
          <X className="w-4 h-4" />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          asChild
          className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
        >
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="w-4 h-4" />
          </a>
        </Button>
      </div>
    </motion.div>
  );
};
