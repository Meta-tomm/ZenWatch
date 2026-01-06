'use client';

import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { authApi } from '@/lib/api-client';
import { useAuthStore } from '@/store/auth-store';

export const useCurrentUser = () => {
  const { user, accessToken, isAuthenticated, isLoading, setUser, setLoading, logout } = useAuthStore();

  const { data, isLoading: isQueryLoading, error } = useQuery({
    queryKey: ['user', 'me'],
    queryFn: () => authApi.getMe(),
    enabled: !!accessToken && !user,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (data) {
      setUser(data);
      setLoading(false);
    }
  }, [data, setUser, setLoading]);

  useEffect(() => {
    if (error) {
      logout();
    }
  }, [error, logout]);

  useEffect(() => {
    if (!accessToken) {
      setLoading(false);
    }
  }, [accessToken, setLoading]);

  return {
    user,
    isAuthenticated,
    isLoading: isLoading || isQueryLoading,
  };
};
