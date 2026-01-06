'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userKeywordsApi } from '@/lib/api-client';
import type { UserKeywordCreate } from '@/types/auth';

export const useUserKeywords = () => {
  const queryClient = useQueryClient();
  const queryKey = ['user-keywords'];

  const { data, isLoading, error } = useQuery({
    queryKey,
    queryFn: () => userKeywordsApi.list(),
  });

  const keywords = data?.data || [];

  const createMutation = useMutation({
    mutationFn: (data: UserKeywordCreate) => userKeywordsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => userKeywordsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  });

  const addKeyword = (keyword: string, weight?: number, category?: string) => {
    createMutation.mutate({ keyword, weight, category });
  };

  const removeKeyword = (id: number) => {
    deleteMutation.mutate(id);
  };

  return {
    keywords,
    isLoading,
    error,
    addKeyword,
    removeKeyword,
    isAdding: createMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
};
