'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, Trophy, Star, BookmarkPlus } from 'lucide-react';
import { CornerBrackets } from '@/components/cyberpunk';
import { LikeDislikeButtons } from '@/components/feed/LikeDislikeButtons';
import { Skeleton } from '@/components/ui/skeleton';
import { formatRelativeDate } from '@/lib/date-utils';
import { articlesApi } from '@/lib/api-client';
import { cn } from '@/lib/utils';
import type { Article } from '@/types';

export const BestArticleCard = () => {
  const [article, setArticle] = useState<Article | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBestArticle = async () => {
      try {
        setIsLoading(true);
        const bestArticle = await articlesApi.getBestOfWeek();
        setArticle(bestArticle);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch best article:', err);
        setError('Failed to load article');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBestArticle();
  }, []);

  const handleToggleFavorite = async () => {
    if (!article) return;
    try {
      const updated = await articlesApi.toggleFavorite(article.id);
      setArticle(updated);
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const handleLike = async () => {
    if (!article) return;
    try {
      const updated = await articlesApi.toggleLike(article.id);
      setArticle(updated);
    } catch (err) {
      console.error('Failed to like article:', err);
    }
  };

  const handleDislike = async () => {
    if (!article) return;
    try {
      const updated = await articlesApi.toggleDislike(article.id);
      setArticle(updated);
    } catch (err) {
      console.error('Failed to dislike article:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="w-full">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="w-6 h-6 text-gold-light" />
          <h2 className="text-2xl font-bold">Article of the Week</h2>
        </div>
        <CornerBrackets color="gold-light">
          <div className="bg-charcoal-900/50 border border-gold-light/30 p-6 space-y-4">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-20 w-full" />
            <div className="flex gap-2">
              <Skeleton className="h-6 w-20" />
              <Skeleton className="h-6 w-20" />
            </div>
          </div>
        </CornerBrackets>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="w-full">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="w-6 h-6 text-gold-light" />
          <h2 className="text-2xl font-bold">Article of the Week</h2>
        </div>
        <CornerBrackets color="gold-light">
          <div className="bg-charcoal-900/50 border border-gold-light/30 p-6">
            <p className="text-center text-muted-foreground">
              {error || 'No articles available'}
            </p>
          </div>
        </CornerBrackets>
      </div>
    );
  }

  const scoreColor = article.score >= 70 ? 'text-gold' : article.score >= 50 ? 'text-gold-light' : 'text-muted-foreground';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <div className="flex items-center gap-2 mb-4">
        <Trophy className="w-6 h-6 text-gold-light animate-pulse" />
        <h2 className="text-2xl font-bold glow-text">Article of the Week</h2>
      </div>

      <CornerBrackets color="gold-light">
        <div className="bg-charcoal-900/50 border border-gold-light/30 backdrop-blur-sm p-6 hover:bg-charcoal-800/70 hover:border-gold-light/50 transition-all">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex-1">
              <h3 className="text-2xl font-bold leading-tight mb-2 glow-text">
                {article.title}
              </h3>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span className="capitalize">{article.source_type}</span>
                <span>•</span>
                <span>{formatRelativeDate(article.published_at)}</span>
                {article.read_time_minutes && (
                  <>
                    <span>•</span>
                    <span>{article.read_time_minutes} min read</span>
                  </>
                )}
              </div>
            </div>

            {/* Score */}
            <div className="flex flex-col items-center shrink-0">
              <div className={cn('text-4xl font-bold', scoreColor)}>
                {article.score.toFixed(0)}
              </div>
              <div className="text-xs text-muted-foreground">score</div>
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mb-4">
            <Badge variant="default" className="text-sm">
              {article.category}
            </Badge>
            {(article.tags || []).slice(0, 5).map((tag) => (
              <Badge key={tag} variant="outline" className="text-sm">
                {tag}
              </Badge>
            ))}
          </div>

          {/* Summary */}
          {article.summary && (
            <p className="text-base text-muted-foreground leading-relaxed mb-4">
              {article.summary}
            </p>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between border-t border-gold/20 pt-4">
            <LikeDislikeButtons
              initialLikes={article.likes}
              initialDislikes={article.dislikes}
              userReaction={article.user_reaction}
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
                    article.is_favorite && 'fill-gold text-gold-light'
                  )}
                />
              </Button>
              <Button variant="ghost" size="default">
                <BookmarkPlus className="w-5 h-5" />
              </Button>
              <Button variant="default" asChild>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="gap-2"
                >
                  Read Article
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
