import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { triageApi, libraryApi } from '@/lib/api-client';
import { toast } from '@/hooks/use-toast';
import type { Article } from '@/types';

export const useTriage = (limit: number = 10) => {
  return useQuery({
    queryKey: ['triage', limit],
    queryFn: () => triageApi.getTriage(limit),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useDismissArticle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => triageApi.dismiss(articleId),

    onMutate: async (articleId) => {
      await queryClient.cancelQueries({ queryKey: ['triage'] });

      const previousTriage = queryClient.getQueryData(['triage']);

      // Optimistic removal from triage
      queryClient.setQueriesData<any>({ queryKey: ['triage'] }, (old: any) => {
        if (!old) return old;
        return {
          ...old,
          items: old.items.filter((article: Article) => article.id !== articleId),
          remaining_count: old.remaining_count - 1,
        };
      });

      return { previousTriage };
    },

    onError: (_err, _variables, context) => {
      if (context?.previousTriage) {
        queryClient.setQueryData(['triage'], context.previousTriage);
      }
      toast({
        title: "Erreur",
        description: "Impossible de rejeter l'article",
        variant: "destructive",
      });
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['triage'] });
    },
  });
};

export const useTriageBookmark = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => libraryApi.toggleBookmark(articleId),

    onMutate: async (articleId) => {
      await queryClient.cancelQueries({ queryKey: ['triage'] });
      await queryClient.cancelQueries({ queryKey: ['library'] });

      const previousTriage = queryClient.getQueryData(['triage']);
      const previousLibrary = queryClient.getQueryData(['library']);

      // Optimistic removal from triage (bookmarked items leave triage)
      queryClient.setQueriesData<any>({ queryKey: ['triage'] }, (old: any) => {
        if (!old) return old;
        return {
          ...old,
          items: old.items.filter((article: Article) => article.id !== articleId),
          remaining_count: old.remaining_count - 1,
        };
      });

      return { previousTriage, previousLibrary };
    },

    onError: (_err, _variables, context) => {
      if (context?.previousTriage) {
        queryClient.setQueryData(['triage'], context.previousTriage);
      }
      if (context?.previousLibrary) {
        queryClient.setQueryData(['library'], context.previousLibrary);
      }
      toast({
        title: "Erreur",
        description: "Impossible d'ajouter a la bibliotheque",
        variant: "destructive",
      });
    },

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['triage'] });
      queryClient.invalidateQueries({ queryKey: ['library'] });
      toast({
        title: "Ajoute a la bibliotheque",
        description: "L'article a ete sauvegarde",
      });
    },
  });
};
