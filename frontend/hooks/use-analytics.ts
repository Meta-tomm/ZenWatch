'use client';

import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/lib/api-client';

export const useAnalyticsSummary = () => {
  return useQuery({
    queryKey: ['analytics', 'summary'],
    queryFn: () => analyticsApi.getSummary(),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Auto-refresh every minute for real-time feel
  });
};

export const useDailyStats = (days: number = 7) => {
  return useQuery({
    queryKey: ['analytics', 'daily-stats', days],
    queryFn: () => analyticsApi.getDailyStats(days),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useTrends = (days: number = 7, limit: number = 20) => {
  return useQuery({
    queryKey: ['analytics', 'trends', days, limit],
    queryFn: () => analyticsApi.getTrends(days, limit),
    staleTime: 5 * 60 * 1000,
  });
};

export const useTopKeywords = (days: number = 7, limit: number = 10) => {
  return useQuery({
    queryKey: ['analytics', 'top-keywords', days, limit],
    queryFn: () => analyticsApi.getTopKeywords(days, limit),
    staleTime: 5 * 60 * 1000,
  });
};
