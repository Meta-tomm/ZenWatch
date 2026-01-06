'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ProfileCard } from '@/components/profile';
import { authApi } from '@/lib/api-client';
import { useCurrentUser } from '@/hooks/use-current-user';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

interface ProfilePageProps {
  params: Promise<{ username: string }>;
}

export default function PublicProfilePage({ params }: ProfilePageProps) {
  const resolvedParams = use(params);
  const { user: currentUser } = useCurrentUser();

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['user', 'profile', resolvedParams.username],
    queryFn: () => authApi.getPublicProfile(resolvedParams.username),
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Card>
          <CardHeader>
            <div className="flex gap-4">
              <Skeleton className="h-20 w-20 rounded-full" />
              <div className="space-y-2">
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-4 w-64" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Skeleton className="h-4 w-32" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Card>
          <CardContent className="py-12 text-center">
            <h2 className="text-xl font-semibold mb-2">Profil introuvable</h2>
            <p className="text-muted-foreground">
              Lutilisateur @{resolvedParams.username} nexiste pas
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isCurrentUser = currentUser?.id === profile.id;

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <ProfileCard profile={profile} isCurrentUser={isCurrentUser} />
    </div>
  );
}
