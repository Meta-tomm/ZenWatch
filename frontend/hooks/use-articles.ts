import { useInfiniteQuery } from '@tanstack/react-query';
import { articlesApi } from '@/lib/api-client';
import type { ArticleFilters } from '@/types';

export const useArticles = (filters: ArticleFilters) => {
  return useInfiniteQuery({
    queryKey: ['articles', filters],
    queryFn: async ({ pageParam = 0 }) => {
      const response = await articlesApi.getArticles({
        ...filters,
        offset: pageParam,
        limit: 50,
      });
      return response;
    },
    getNextPageParam: (lastPage, allPages) => {
      return lastPage.hasMore ? allPages.length * 50 : undefined;
    },
    initialPageParam: 0,
  });
};
