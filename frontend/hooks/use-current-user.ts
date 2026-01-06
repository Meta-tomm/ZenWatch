// frontend/hooks/use-current-user.ts

import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth-store';
import { usersApi } from '@/lib/api-client';
import { useEffect } from 'react';

export const useCurrentUser = () => {
  const { user, isAuthenticated, accessToken, setUser, setLoading, clearAuth } = useAuthStore();

  const query = useQuery({
    queryKey: ['user', 'me'],
    queryFn: usersApi.getMe,
    enabled: isAuthenticated && !!accessToken,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  });

  // Sync query data with store
  useEffect(() => {
    if (query.data) {
      setUser(query.data);
    }
  }, [query.data, setUser]);

  // Handle auth errors
  useEffect(() => {
    if (query.error) {
      clearAuth();
    }
  }, [query.error, clearAuth]);

  // Set loading state based on query
  useEffect(() => {
    setLoading(query.isLoading);
  }, [query.isLoading, setLoading]);

  return {
    user: query.data ?? user,
    isLoading: query.isLoading,
    isAuthenticated,
    refetch: query.refetch,
  };
};
