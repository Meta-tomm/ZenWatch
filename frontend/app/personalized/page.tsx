'use client';

import { useQuery } from '@tanstack/react-query';
import { personalizedApi, userKeywordsApi } from '@/lib/api-client';
import { useUIStore } from '@/store/ui-store';
import { useModalsStore } from '@/store/modals-store';
import { ArticleCard } from '@/components/feed/ArticleCard';
import { ArticleModal } from '@/components/feed/ArticleModal';
import { FilterBar } from '@/components/feed/FilterBar';
import { AuthGuard } from '@/components/auth';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Virtuoso } from 'react-virtuoso';
import { AlertCircle, Sparkles, Tags, ArrowLeft, Settings } from 'lucide-react';
import Link from 'next/link';

export default function PersonalizedPage() {
  const activeFilters = useUIStore((s) => s.activeFilters);
  const openArticleModal = useModalsStore((s) => s.openArticleModal);

  // Fetch keywords to show status
  const { data: keywordsData } = useQuery({
    queryKey: ['user-keywords'],
    queryFn: userKeywordsApi.list,
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['personalized-stats'],
    queryFn: personalizedApi.getStats,
  });

  // Fetch personalized feed
  const {
    data: feedData,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['personalized-feed', activeFilters],
    queryFn: () =>
      personalizedApi.getFeed({
        search: activeFilters.search,
        categories: activeFilters.categories,
        sources: activeFilters.sources,
        timeRange: activeFilters.timeRange,
      }),
  });

  const articles = feedData?.data ?? [];
  const keywords = keywordsData?.data ?? [];
  const hasKeywords = keywords.length > 0;

  return (
    <AuthGuard>
      <main className="min-h-screen bg-anthracite-950">
        {/* Header */}
        <div className="sticky top-0 z-40 border-b border-violet-500/20 bg-anthracite-900/95 backdrop-blur supports-[backdrop-filter]:bg-anthracite-900/80">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link href="/">
                  <Button variant="ghost" size="sm" className="gap-2 text-violet-300 hover:text-violet-200 hover:bg-violet-500/20">
                    <ArrowLeft className="w-4 h-4" />
                    Accueil
                  </Button>
                </Link>
                <h1 className="text-2xl font-bold text-gradient-violet flex items-center gap-2">
                  <Sparkles className="w-6 h-6" />
                  Pour Vous
                </h1>
              </div>
              <div className="flex items-center gap-3">
                {stats && (
                  <div className="hidden md:flex items-center gap-3">
                    <Badge variant="secondary" className="bg-violet-500/20 text-violet-300 border-violet-500/30">
                      {stats.keyword_count} mot{stats.keyword_count > 1 ? 's' : ''}-cle{stats.keyword_count > 1 ? 's' : ''}
                    </Badge>
                    <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30">
                      {stats.high_relevance_count} haute pertinence
                    </Badge>
                  </div>
                )}
                <Link href="/profile">
                  <Button variant="outline" size="sm" className="gap-2 border-violet-500/30 text-violet-300 hover:bg-violet-500/20">
                    <Settings className="w-4 h-4" />
                    Configurer
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* No keywords warning */}
        {!hasKeywords && !isLoading && (
          <div className="container mx-auto px-4 py-8">
            <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 p-8 text-center">
              <Tags className="w-16 h-16 mx-auto mb-4 text-violet-400/50" />
              <h2 className="text-xl font-semibold text-violet-100 mb-2">
                Configurez vos mots-cles
              </h2>
              <p className="text-violet-300/60 mb-6 max-w-md mx-auto">
                Ajoutez des mots-cles pour personnaliser votre feed.
                Les articles seront tries par pertinence selon vos centres d&apos;interet.
              </p>
              <Link href="/profile">
                <Button className="bg-violet-600 hover:bg-violet-500 text-white gap-2">
                  <Tags className="w-4 h-4" />
                  Configurer mes mots-cles
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* Filter Bar */}
        {hasKeywords && <FilterBar />}

        {/* Feed */}
        {hasKeywords && (
          <div className="h-[calc(100vh-12rem)]">
            {isLoading ? (
              <div className="p-4 space-y-4">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-48 w-full" />
                ))}
              </div>
            ) : isError ? (
              <div className="flex flex-col items-center justify-center h-full text-center p-8">
                <AlertCircle className="w-12 h-12 text-destructive mb-4" />
                <h2 className="text-lg font-semibold mb-2">Erreur de chargement</h2>
                <p className="text-sm text-muted-foreground">
                  {String(error)}
                </p>
              </div>
            ) : articles.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center p-8">
                <h2 className="text-lg font-semibold mb-2">Aucun article trouve</h2>
                <p className="text-sm text-muted-foreground">
                  Essayez de modifier vos filtres
                </p>
              </div>
            ) : (
              <Virtuoso
                data={articles}
                itemContent={(_index, article) => (
                  <div className="px-4 py-2">
                    <div className="relative">
                      {/* Personalized score badge */}
                      {article.personalized_score !== null && article.personalized_score !== undefined && (
                        <div className="absolute top-2 right-2 z-10">
                          <Badge
                            className={
                              article.personalized_score >= 70
                                ? 'bg-green-500/90 text-white border-green-400'
                                : article.personalized_score >= 40
                                  ? 'bg-violet-500/90 text-white border-violet-400'
                                  : 'bg-anthracite-700/90 text-violet-200 border-violet-500/30'
                            }
                          >
                            <Sparkles className="w-3 h-3 mr-1" />
                            {Math.round(article.personalized_score)}
                          </Badge>
                        </div>
                      )}
                      <ArticleCard
                        article={article}
                        onOpenModal={openArticleModal}
                      />
                    </div>
                  </div>
                )}
              />
            )}
          </div>
        )}

        {/* Article Modal */}
        <ArticleModal />
      </main>
    </AuthGuard>
  );
}
