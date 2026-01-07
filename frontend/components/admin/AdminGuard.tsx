'use client';

import { useEffect, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useCurrentUser } from '@/hooks/use-current-user';
import { Skeleton } from '@/components/ui/skeleton';
import { ShieldAlert } from 'lucide-react';

interface AdminGuardProps {
  children: ReactNode;
}

export const AdminGuard = ({ children }: AdminGuardProps) => {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useCurrentUser();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push('/login');
      } else if (!user?.is_admin) {
        router.push('/');
      }
    }
  }, [isAuthenticated, isLoading, user, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-anthracite-950">
        <div className="space-y-4 w-full max-w-md p-8">
          <Skeleton className="h-8 w-3/4 mx-auto bg-violet-500/20" />
          <Skeleton className="h-4 w-1/2 mx-auto bg-violet-500/10" />
          <div className="space-y-3 pt-4">
            <Skeleton className="h-10 w-full bg-violet-500/10" />
            <Skeleton className="h-10 w-full bg-violet-500/10" />
            <Skeleton className="h-10 w-full bg-violet-500/10" />
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user?.is_admin) {
    return (
      <div className="flex h-screen items-center justify-center bg-anthracite-950">
        <div className="text-center space-y-4 p-8">
          <ShieldAlert className="w-16 h-16 text-red-400 mx-auto" />
          <h1 className="text-2xl font-bold text-violet-100">Acces refuse</h1>
          <p className="text-violet-300/60">
            Vous n'avez pas les permissions necessaires pour acceder a cette page.
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
