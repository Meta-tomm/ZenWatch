import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { libraryApi } from '@/lib/api-client';
import { toast } from '@/hooks/use-toast';
import type { Article, LibraryFilter } from '@/types';

interface LibraryParams {
  type?: LibraryFilter;
  unread_only?: boolean;
}

export const useLibrary = (params?: LibraryParams) => {
  return useQuery({
    queryKey: ['library', params],
    queryFn: () => libraryApi.getLibrary(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useToggleBookmark = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => libraryApi.toggleBookmark(articleId),

    onMutate: async (articleId) => {
      await queryClient.cancelQueries({ queryKey: ['articles'] });
      await queryClient.cancelQueries({ queryKey: ['library'] });

      const previousArticles = queryClient.getQueryData(['articles']);
      const previousLibrary = queryClient.getQueryData(['library']);

      // Optimistic update for articles list
      queryClient.setQueriesData<any>({ queryKey: ['articles'] }, (old: any) => {
        if (!old) return old;
        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            data: page.data.map((article: Article) =>
              article.id === articleId
                ? { ...article, is_bookmarked: !article.is_bookmarked }
                : article
            ),
          })),
        };
      });

      return { previousArticles, previousLibrary };
    },

    onError: (_err, _variables, context) => {
      if (context?.previousArticles) {
        queryClient.setQueryData(['articles'], context.previousArticles);
      }
      if (context?.previousLibrary) {
        queryClient.setQueryData(['library'], context.previousLibrary);
      }
      toast({
        title: "Erreur",
        description: "Impossible de mettre a jour la bibliotheque",
        variant: "destructive",
      });
    },

    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['library'] });
      toast({
        title: data.is_bookmarked ? "Ajoute a la bibliotheque" : "Retire de la bibliotheque",
        description: data.is_bookmarked
          ? "L'article a ete ajoute a votre bibliotheque"
          : "L'article a ete retire de votre bibliotheque",
      });
    },
  });
};

export const useRemoveFromLibrary = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => libraryApi.toggleBookmark(articleId),

    onMutate: async (articleId) => {
      await queryClient.cancelQueries({ queryKey: ['library'] });

      const previousLibrary = queryClient.getQueryData(['library']);

      // Optimistic removal from library
      queryClient.setQueriesData<any>({ queryKey: ['library'] }, (old: any) => {
        if (!old) return old;
        return {
          ...old,
          items: old.items.filter((article: Article) => article.id !== articleId),
          total: old.total - 1,
        };
      });

      return { previousLibrary };
    },

    onError: (_err, _variables, context) => {
      if (context?.previousLibrary) {
        queryClient.setQueryData(['library'], context.previousLibrary);
      }
      toast({
        title: "Erreur",
        description: "Impossible de retirer l'article",
        variant: "destructive",
      });
    },

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['library'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      toast({
        title: "Retire de la bibliotheque",
        description: "L'article a ete retire de votre bibliotheque",
      });
    },
  });
};
