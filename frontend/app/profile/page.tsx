'use client';

import { useState } from 'react';
import { AuthGuard } from '@/components/auth';
import { ProfileCard, ProfileEditForm } from '@/components/profile';
import { useCurrentUser } from '@/hooks/use-current-user';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export default function ProfilePage() {
  const { user, isLoading } = useCurrentUser();
  const [isEditing, setIsEditing] = useState(false);

  return (
    <AuthGuard>
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <h1 className="text-3xl font-bold mb-6">Mon Profil</h1>

        {isLoading ? (
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
        ) : user ? (
          isEditing ? (
            <Card>
              <CardHeader>
                <CardTitle>Modifier mon profil</CardTitle>
              </CardHeader>
              <CardContent>
                <ProfileEditForm
                  user={user}
                  onSuccess={() => setIsEditing(false)}
                  onCancel={() => setIsEditing(false)}
                />
              </CardContent>
            </Card>
          ) : (
            <ProfileCard
              profile={user}
              isCurrentUser
              onEdit={() => setIsEditing(true)}
            />
          )
        ) : (
          <p className="text-muted-foreground">Utilisateur non trouve</p>
        )}
      </div>
    </AuthGuard>
  );
}
