'use client';

import { useEffect, useRef } from 'react';
import { useRouter, useSearchParams, useParams } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';

export default function OAuthCallbackPage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const { setAuth, setLoading } = useAuthStore();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const provider = params.provider as string;
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code || !state) {
      console.error('Missing code or state');
      router.push('/login?error=missing_params');
      return;
    }

    const handleCallback = async () => {
      try {
        setLoading(true);

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
        const response = await fetch(
          `${apiUrl}/auth/oauth/${provider}/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`,
          {
            method: 'GET',
            credentials: 'include',
          }
        );

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'OAuth callback failed');
        }

        const data = await response.json();

        setAuth(data.user, data.access_token);
        router.push('/');
      } catch (error) {
        console.error('OAuth callback error:', error);
        router.push('/login?error=oauth_failed');
      } finally {
        setLoading(false);
      }
    };

    handleCallback();
  }, [params, searchParams, router, setAuth, setLoading]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-anthracite-950">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-violet-500 mx-auto mb-4" />
        <p className="text-violet-200">Connexion en cours...</p>
      </div>
    </div>
  );
}
