'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, ExternalLink, MessageSquare, TrendingUp, BookmarkPlus } from 'lucide-react';
import { useToggleFavorite } from '@/hooks/use-toggle-favorite';
import { formatRelativeDate } from '@/lib/date-utils';
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

  return (
    <Card
      className={cn(
        'transition-all hover:shadow-md',
        article.is_read && 'opacity-60'
      )}
    >
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex-1 min-w-0">
            <h3
              className="font-semibold leading-tight mb-1 cursor-pointer hover:text-primary line-clamp-2"
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
          {article.tags.slice(0, 3).map((tag) => (
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
            {article.upvotes}
          </div>
          <div className="flex items-center gap-1">
            <MessageSquare className="w-3 h-3" />
            {article.comments_count}
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
      </CardContent>
    </Card>
  );
};
