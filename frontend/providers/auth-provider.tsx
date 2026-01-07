'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/auth-store';
import { authApi } from '@/lib/api-client';

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [isHydrated, setIsHydrated] = useState(false);
  const { accessToken, setAuth, setLoading, logout } = useAuthStore();

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      if (!isHydrated) return;

      if (accessToken) {
        try {
          const user = await authApi.getMe();
          setAuth(user, accessToken);
        } catch {
          logout();
        }
      } else {
        setLoading(false);
      }
    };

    initAuth();
  }, [isHydrated, accessToken, setAuth, setLoading, logout]);

  // Prevent flash of wrong content
  if (!isHydrated) {
    return null;
  }

  return <>{children}</>;
}
