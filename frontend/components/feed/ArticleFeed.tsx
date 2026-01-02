'use client';

import { useArticles } from '@/hooks/use-articles';
import { useUIStore } from '@/store/ui-store';
import { useModalsStore } from '@/store/modals-store';
import { ArticleCard } from './ArticleCard';
import { Skeleton } from '@/components/ui/skeleton';
import { Virtuoso } from 'react-virtuoso';
import { AlertCircle } from 'lucide-react';

export const ArticleFeed = () => {
  const activeFilters = useUIStore((s) => s.activeFilters);
  const openArticleModal = useModalsStore((s) => s.openArticleModal);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
  } = useArticles({
    search: activeFilters.search,
    categories: activeFilters.categories,
    sources: activeFilters.sources,
    sort: activeFilters.sort,
  });

  const allArticles = data?.pages.flatMap((page) => page.data) ?? [];

  if (isLoading) {
    return (
      <div className="p-4 space-y-4">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-48 w-full" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <AlertCircle className="w-12 h-12 text-destructive mb-4" />
        <h2 className="text-lg font-semibold mb-2">Erreur de chargement</h2>
        <p className="text-sm text-muted-foreground">
          Impossible de charger les articles. Veuillez réessayer.
        </p>
      </div>
    );
  }

  if (allArticles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <h2 className="text-lg font-semibold mb-2">Aucun article trouvé</h2>
        <p className="text-sm text-muted-foreground">
          Essayez de modifier vos filtres ou mots-clés
        </p>
      </div>
    );
  }

  return (
    <Virtuoso
      data={allArticles}
      endReached={() => {
        if (hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      }}
      itemContent={(_index, article) => (
        <div className="px-4 py-2">
          <ArticleCard
            article={article}
            onOpenModal={openArticleModal}
          />
        </div>
      )}
      components={{
        Footer: () =>
          isFetchingNextPage ? (
            <div className="p-4">
              <Skeleton className="h-48 w-full" />
            </div>
          ) : null,
      }}
    />
  );
};
