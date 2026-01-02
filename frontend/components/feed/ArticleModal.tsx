'use client';

import { useQuery } from '@tanstack/react-query';
import { useModalsStore } from '@/store/modals-store';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ExternalLink, Star, BookmarkPlus } from 'lucide-react';
import { formatDate } from '@/lib/date-utils';
import { useToggleFavorite } from '@/hooks/use-toggle-favorite';
import type { Article } from '@/types';

export const ArticleModal = () => {
  const { articleModal, closeArticleModal } = useModalsStore();
  const toggleFavorite = useToggleFavorite();

  const { data: article, isLoading } = useQuery<Article | null>({
    queryKey: ['article', articleModal.articleId],
    queryFn: async () => {
      // TODO: Replace with actual API call when backend ready
      // For now, we'll get from cache
      return null;
    },
    enabled: articleModal.open && !!articleModal.articleId,
  });

  return (
    <Dialog open={articleModal.open} onOpenChange={closeArticleModal}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : article ? (
          <>
            <DialogHeader>
              <DialogTitle className="text-2xl leading-tight pr-8">
                {article.title}
              </DialogTitle>
            </DialogHeader>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <span className="capitalize">{article.source_type}</span>
              <span>•</span>
              <span>{formatDate(article.published_at)}</span>
              {article.author && (
                <>
                  <span>•</span>
                  <span>Par {article.author}</span>
                </>
              )}
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2">
              <Badge>{article.category}</Badge>
              {article.tags.map((tag) => (
                <Badge key={tag} variant="outline">
                  {tag}
                </Badge>
              ))}
            </div>

            {/* Score */}
            <div className="flex items-center gap-4 p-4 bg-muted rounded-lg">
              <div>
                <div className="text-3xl font-bold text-primary">
                  {article.score.toFixed(0)}
                </div>
                <div className="text-xs text-muted-foreground">Score</div>
              </div>
              <div className="flex-1 text-sm text-muted-foreground">
                Basé sur vos mots-clés et préférences
              </div>
            </div>

            {/* Summary */}
            {article.summary && (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <h3 className="text-lg font-semibold mb-2">Résumé IA</h3>
                <p className="leading-relaxed">{article.summary}</p>
              </div>
            )}

            {/* Content */}
            {article.content && (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <h3 className="text-lg font-semibold mb-2">Contenu</h3>
                <div
                  className="leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: article.content }}
                />
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-2 pt-4 border-t">
              <Button
                variant="outline"
                onClick={() => toggleFavorite.mutate(article.id)}
              >
                <Star
                  className={
                    article.is_favorite ? 'fill-yellow-500 text-yellow-500' : ''
                  }
                />
                {article.is_favorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
              </Button>
              <Button variant="outline">
                <BookmarkPlus className="w-4 h-4 mr-2" />
                Archiver
              </Button>
              <Button asChild className="ml-auto">
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Lire l'article
                </a>
              </Button>
            </div>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
};
