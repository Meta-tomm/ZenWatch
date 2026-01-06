// frontend/hooks/use-auth.ts

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';
import { authApi } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { LoginRequest, RegisterRequest, OAuthProvider } from '@/types/auth';

export const useAuth = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { setAuth, logout: clearAuth, setLoading } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      setAuth(response.user, response.tokens.access_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
      toast({
        title: 'Welcome back!',
        description: `Logged in as ${response.user.username}`,
      });
      router.push('/');
    },
    onError: (error: Error) => {
      toast({
        title: 'Login failed',
        description: error.message || 'Invalid credentials',
        variant: 'destructive',
      });
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (response) => {
      setAuth(response.user, response.tokens.access_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
      toast({
        title: 'Account created!',
        description: 'Welcome to ZenWatch',
      });
      router.push('/');
    },
    onError: (error: Error) => {
      toast({
        title: 'Registration failed',
        description: error.message || 'Could not create account',
        variant: 'destructive',
      });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      clearAuth();
      queryClient.clear();
      toast({
        title: 'Logged out',
        description: 'See you soon!',
      });
      router.push('/login');
    },
    onError: () => {
      // Even if logout fails on server, clear local state
      clearAuth();
      queryClient.clear();
      router.push('/login');
    },
  });

  const loginWithOAuth = (provider: OAuthProvider) => {
    setLoading(true);
    const redirectUrl = authApi.oauthRedirect(provider);
    window.location.href = redirectUrl;
  };

  return {
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
    loginWithOAuth,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
  };
};
