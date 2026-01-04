'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, ExternalLink, MessageSquare, TrendingUp, BookmarkPlus } from 'lucide-react';
import { CornerBrackets } from '@/components/cyberpunk';
import { useToggleFavorite } from '@/hooks/use-toggle-favorite';
import { formatRelativeDate } from '@/lib/date-utils';
import { fadeInScale } from '@/lib/animations';
import { cn } from '@/lib/utils';
import type { Article } from '@/types';

interface ArticleCardProps {
  article: Article;
  onOpenModal?: (id: string) => void;
}

export const ArticleCard = ({ article, onOpenModal }: ArticleCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const toggleFavorite = useToggleFavorite();

  const scoreColor = article.score >= 70 ? 'text-green-500' : article.score >= 50 ? 'text-yellow-500' : 'text-muted-foreground';

  // Determine CornerBrackets color based on score
  const bracketColor = article.score >= 70 ? 'blue' : article.score >= 50 ? 'yellow' : 'green';

  return (
    <motion.div variants={fadeInScale} initial="hidden" animate="visible">
      <CornerBrackets color={bracketColor}>
        <div
          className={cn(
            'p-4 bg-cyber-black/50 border border-cyber-blue/30 backdrop-blur-sm',
            'hover:bg-cyber-black/70 hover:border-cyber-blue/50 transition-all',
            article.is_read && 'opacity-60'
          )}
        >
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex-1 min-w-0">
            <h3
              className={cn(
                'font-semibold leading-tight mb-1 cursor-pointer hover:text-primary line-clamp-2',
                article.score >= 70 && 'glow-text'
              )}
              onClick={() => onOpenModal?.(article.id)}
            >
              {article.title}
            </h3>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="capitalize">{article.source_type}</span>
              <span>•</span>
              <span>{formatRelativeDate(article.published_at)}</span>
              {article.read_time_minutes && (
                <>
                  <span>•</span>
                  <span>{article.read_time_minutes} min</span>
                </>
              )}
            </div>
          </div>

          {/* Score */}
          <div className="flex flex-col items-center shrink-0">
            <div className={cn('text-2xl font-bold', scoreColor)}>
              {article.score.toFixed(0)}
            </div>
            <div className="text-xs text-muted-foreground">score</div>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          <Badge variant="secondary" className="text-xs">
            {article.category}
          </Badge>
          {(article.tags || []).slice(0, 3).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>

        {/* Summary */}
        {article.summary && (
          <p
            className={cn(
              'text-sm text-muted-foreground leading-relaxed mb-3',
              !isExpanded && 'line-clamp-2'
            )}
          >
            {article.summary}
          </p>
        )}

        {/* Stats */}
        <div className="flex items-center gap-4 mb-3 text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            {article.upvotes || 0}
          </div>
          <div className="flex items-center gap-1">
            <MessageSquare className="w-3 h-3" />
            {article.comments_count || 0}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between border-t pt-3">
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleFavorite.mutate(article.id)}
            >
              <Star
                className={cn(
                  'w-4 h-4',
                  article.is_favorite && 'fill-yellow-500 text-yellow-500'
                )}
              />
            </Button>
            <Button variant="ghost" size="sm">
              <BookmarkPlus className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex items-center gap-1">
            {article.summary && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? 'Réduire' : 'Voir plus'}
              </Button>
            )}
            <Button variant="ghost" size="sm" asChild>
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </Button>
          </div>
        </div>
        </div>
      </CornerBrackets>
    </motion.div>
  );
};
