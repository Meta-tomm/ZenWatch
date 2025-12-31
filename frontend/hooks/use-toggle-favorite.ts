import { useMutation, useQueryClient } from '@tanstack/react-query';
import { articlesApi } from '@/lib/api-client';
import { toast } from '@/hooks/use-toast';
import type { Article } from '@/types';

export const useToggleFavorite = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => articlesApi.toggleFavorite(articleId),

    onMutate: async (articleId) => {
      await queryClient.cancelQueries({ queryKey: ['articles'] });

      const previousData = queryClient.getQueryData(['articles']);

      queryClient.setQueriesData<any>({ queryKey: ['articles'] }, (old: any) => {
        if (!old) return old;
        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            data: page.data.map((article: Article) =>
              article.id === articleId
                ? { ...article, is_favorite: !article.is_favorite }
                : article
            ),
          })),
        };
      });

      return { previousData };
    },

    onError: (_err, _variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(['articles'], context.previousData);
      }
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour les favoris",
        variant: "destructive",
      });
    },

    onSuccess: () => {
      toast({
        title: "Favoris mis à jour",
        description: "L'article a été ajouté/retiré des favoris",
      });
    },
  });
};
