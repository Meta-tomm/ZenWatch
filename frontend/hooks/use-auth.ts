'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api-client';
import { useAuthStore } from '@/store/auth-store';
import type { LoginRequest, RegisterRequest } from '@/types/auth';

export const useAuth = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { setAuth, logout: storeLogout, setLoading } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      setAuth(response.user, response.tokens.access_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
      router.push('/');
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (response) => {
      setAuth(response.user, response.tokens.access_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
      router.push('/');
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      storeLogout();
      queryClient.clear();
      router.push('/login');
    },
    onError: () => {
      storeLogout();
      queryClient.clear();
      router.push('/login');
    },
  });

  const loginWithOAuth = (provider: 'github' | 'google' | 'discord') => {
    setLoading(true);
    window.location.href = authApi.oauthRedirect(provider);
  };

  const login = (data: LoginRequest) => loginMutation.mutate(data);
  const register = (data: RegisterRequest) => registerMutation.mutate(data);
  const logout = () => logoutMutation.mutate();

  return {
    login,
    register,
    logout,
    loginWithOAuth,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
  };
};
