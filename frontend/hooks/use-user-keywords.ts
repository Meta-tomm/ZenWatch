// frontend/hooks/use-user-keywords.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userKeywordsApi } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

export const useUserKeywords = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const query = useQuery({
    queryKey: ['user-keywords'],
    queryFn: userKeywordsApi.list,
  });

  const createMutation = useMutation({
    mutationFn: ({ keyword, weight }: { keyword: string; weight?: number }) =>
      userKeywordsApi.create(keyword, weight),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-keywords'] });
      toast({
        title: 'Keyword added',
        description: 'Your personalized keyword has been saved',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Could not add keyword',
        variant: 'destructive',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => userKeywordsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-keywords'] });
      toast({
        title: 'Keyword removed',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Could not remove keyword',
        variant: 'destructive',
      });
    },
  });

  return {
    keywords: query.data ?? [],
    isLoading: query.isLoading,
    error: query.error,
    addKeyword: createMutation.mutate,
    removeKeyword: deleteMutation.mutate,
    isAdding: createMutation.isPending,
    isRemoving: deleteMutation.isPending,
  };
};
