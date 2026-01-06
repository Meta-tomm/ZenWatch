'use client';

import { useEffect, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useCurrentUser } from '@/hooks/use-current-user';
import { Skeleton } from '@/components/ui/skeleton';

interface AuthGuardProps {
  children: ReactNode;
  requireAuth?: boolean;
  redirectTo?: string;
}

export const AuthGuard = ({
  children,
  requireAuth = true,
  redirectTo = '/login',
}: AuthGuardProps) => {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useCurrentUser();

  useEffect(() => {
    if (!isLoading) {
      if (requireAuth && !isAuthenticated) {
        router.push(redirectTo);
      } else if (!requireAuth && isAuthenticated) {
        router.push('/');
      }
    }
  }, [isAuthenticated, isLoading, requireAuth, redirectTo, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="space-y-4 w-full max-w-md p-8">
          <Skeleton className="h-8 w-3/4 mx-auto" />
          <Skeleton className="h-4 w-1/2 mx-auto" />
          <div className="space-y-3 pt-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (requireAuth && !isAuthenticated) {
    return null;
  }

  if (!requireAuth && isAuthenticated) {
    return null;
  }

  return <>{children}</>;
};
