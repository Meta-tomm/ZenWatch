'use client';

import { useState } from 'react';
import { AuthGuard } from '@/components/auth';
import { ProfileEditForm } from '@/components/profile';
import { useCurrentUser } from '@/hooks/use-current-user';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function SettingsPage() {
  const { user, isLoading } = useCurrentUser();
  const { logout, isLoggingOut } = useAuth();
  const [successMessage, setSuccessMessage] = useState('');

  const handleProfileSuccess = () => {
    setSuccessMessage('Profil mis a jour avec succes');
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  return (
    <AuthGuard>
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <h1 className="text-3xl font-bold mb-6">Parametres</h1>

        {successMessage && (
          <div className="mb-4 p-3 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100 rounded-lg text-sm">
            {successMessage}
          </div>
        )}

        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList>
            <TabsTrigger value="profile">Profil</TabsTrigger>
            <TabsTrigger value="account">Compte</TabsTrigger>
          </TabsList>

          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>Informations du profil</CardTitle>
                <CardDescription>
                  Modifiez vos informations publiques
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-4">
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-24 w-full" />
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-10 w-full" />
                  </div>
                ) : user ? (
                  <ProfileEditForm user={user} onSuccess={handleProfileSuccess} />
                ) : null}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="account" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Informations du compte</CardTitle>
                <CardDescription>
                  Details de votre compte ZenWatch
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {isLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-4 w-64" />
                  </div>
                ) : user ? (
                  <>
                    <div>
                      <p className="text-sm font-medium">Email</p>
                      <p className="text-sm text-muted-foreground">{user.email}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Role</p>
                      <p className="text-sm text-muted-foreground capitalize">{user.role}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Verification</p>
                      <p className="text-sm text-muted-foreground">
                        {user.is_verified ? 'Compte verifie' : 'Compte non verifie'}
                      </p>
                    </div>
                  </>
                ) : null}
              </CardContent>
            </Card>

            <Card className="border-destructive">
              <CardHeader>
                <CardTitle className="text-destructive">Zone de danger</CardTitle>
                <CardDescription>
                  Actions irreversibles sur votre compte
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Separator />
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Deconnexion</p>
                    <p className="text-sm text-muted-foreground">
                      Deconnectez-vous de votre compte
                    </p>
                  </div>
                  <Button
                    variant="destructive"
                    onClick={logout}
                    disabled={isLoggingOut}
                  >
                    {isLoggingOut ? 'Deconnexion...' : 'Se deconnecter'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AuthGuard>
  );
}
