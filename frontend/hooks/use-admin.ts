'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminApi, keywordsApi, sourcesApi } from '@/lib/api-client';
import type {
  AdminUserUpdate,
  AdminUsersFilters,
  AdminCommentsFilters,
} from '@/types/admin';
import type { Keyword, Source } from '@/types';

// Users hooks
export const useAdminUsers = (filters?: AdminUsersFilters) => {
  return useQuery({
    queryKey: ['admin', 'users', filters],
    queryFn: () => adminApi.getUsers(filters),
    staleTime: 30 * 1000, // 30 seconds
  });
};

export const useAdminUser = (userId: number) => {
  return useQuery({
    queryKey: ['admin', 'users', userId],
    queryFn: () => adminApi.getUser(userId),
    enabled: !!userId,
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: AdminUserUpdate }) =>
      adminApi.updateUser(userId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
    },
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: number) => adminApi.deleteUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
    },
  });
};

// Comments hooks
export const useAdminComments = (filters?: AdminCommentsFilters) => {
  return useQuery({
    queryKey: ['admin', 'comments', filters],
    queryFn: () => adminApi.getComments(filters),
    staleTime: 30 * 1000,
  });
};

export const useDeleteComment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (commentId: number) => adminApi.deleteComment(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'comments'] });
    },
  });
};

// Scraping hooks
export const useScrapingHistory = (limit: number = 20) => {
  return useQuery({
    queryKey: ['admin', 'scraping', 'history', limit],
    queryFn: () => adminApi.getScrapingHistory(limit),
    staleTime: 10 * 1000, // 10 seconds - refresh more often
    refetchInterval: 30 * 1000, // Auto-refresh every 30s
  });
};

export const useScrapingStats = () => {
  return useQuery({
    queryKey: ['admin', 'scraping', 'stats'],
    queryFn: () => adminApi.getScrapingStats(),
    staleTime: 30 * 1000,
  });
};

export const useTriggerScraping = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (keywords?: string[]) => adminApi.triggerScraping(keywords),
    onSuccess: () => {
      // Invalidate scraping history after triggering
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['admin', 'scraping'] });
      }, 2000);
    },
  });
};

export const useTriggerYouTubeScraping = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => adminApi.triggerYouTubeScraping(),
    onSuccess: () => {
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['admin', 'scraping'] });
      }, 2000);
    },
  });
};

export const useTriggerRescore = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (forceAll: boolean = false) => adminApi.triggerRescore(forceAll),
    onSuccess: () => {
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['admin', 'scraping'] });
      }, 2000);
    },
  });
};

// Keywords hooks (for admin)
export const useAdminKeywords = () => {
  return useQuery({
    queryKey: ['admin', 'keywords'],
    queryFn: () => keywordsApi.getKeywords(),
    staleTime: 60 * 1000, // 1 minute
  });
};

export const useCreateKeyword = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Keyword>) => keywordsApi.createKeyword(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'keywords'] });
      queryClient.invalidateQueries({ queryKey: ['keywords'] });
    },
  });
};

export const useUpdateKeyword = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Keyword> }) =>
      keywordsApi.updateKeyword(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'keywords'] });
      queryClient.invalidateQueries({ queryKey: ['keywords'] });
    },
  });
};

export const useDeleteKeyword = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => keywordsApi.deleteKeyword(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'keywords'] });
      queryClient.invalidateQueries({ queryKey: ['keywords'] });
    },
  });
};

// Sources hooks (for admin)
export const useAdminSources = () => {
  return useQuery({
    queryKey: ['admin', 'sources'],
    queryFn: () => sourcesApi.getSources(),
    staleTime: 60 * 1000,
  });
};

export const useUpdateSource = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Source> }) =>
      sourcesApi.updateSource(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'sources'] });
      queryClient.invalidateQueries({ queryKey: ['sources'] });
    },
  });
};
