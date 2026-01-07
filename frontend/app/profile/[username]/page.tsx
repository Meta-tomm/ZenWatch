'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, UserX } from 'lucide-react';
import { ProfileCard } from '@/components/profile';
import { authApi } from '@/lib/api-client';
import { useCurrentUser } from '@/hooks/use-current-user';
import { Button } from '@/components/ui/button';

export default function PublicProfilePage() {
  const params = useParams<{ username: string }>();
  const username = params.username;
  const { user: currentUser } = useCurrentUser();

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['user', 'profile', username],
    queryFn: () => authApi.getPublicProfile(username),
    enabled: !!username,
  });

  return (
    <main className="min-h-screen bg-anthracite-950">
      {/* Header sticky */}
      <div className="sticky top-0 z-40 border-b border-violet-500/20 bg-anthracite-900/95 backdrop-blur supports-[backdrop-filter]:bg-anthracite-900/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="sm" className="gap-2 text-violet-300 hover:text-violet-200 hover:bg-violet-500/20">
                <ArrowLeft className="w-4 h-4" />
                Accueil
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gradient-violet">
              Profil de @{username}
            </h1>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {isLoading ? (
          <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur overflow-hidden">
            <div className="h-24 bg-gradient-to-r from-violet-600/20 via-purple-600/20 to-fuchsia-600/20" />
            <div className="px-6 pb-6">
              <div className="flex gap-4 -mt-12">
                <div className="h-24 w-24 rounded-full bg-violet-500/20 animate-pulse border-4 border-anthracite-900" />
                <div className="space-y-3 flex-1 pt-14">
                  <div className="h-8 w-48 bg-violet-500/20 rounded animate-pulse" />
                  <div className="h-4 w-64 bg-violet-500/10 rounded animate-pulse" />
                </div>
              </div>
            </div>
          </div>
        ) : error || !profile ? (
          <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur p-12 text-center">
            <UserX className="w-16 h-16 mx-auto text-violet-500/30 mb-4" />
            <h2 className="text-xl font-semibold text-violet-100 mb-2">Profil introuvable</h2>
            <p className="text-violet-300/60">
              L&apos;utilisateur @{username} n&apos;existe pas
            </p>
            <Link href="/">
              <Button variant="outline" className="mt-6 border-violet-500/30 text-violet-300 hover:bg-violet-500/20">
                Retour a l&apos;accueil
              </Button>
            </Link>
          </div>
        ) : (
          <ProfileCard
            profile={profile}
            isCurrentUser={currentUser?.id === profile.id}
          />
        )}
      </div>
    </main>
  );
}
