'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import { authApi } from '@/lib/api-client';
import { useAuthStore } from '@/store/auth-store';
import type { User } from '@/types/auth';

const profileSchema = z.object({
  username: z
    .string()
    .min(3, 'Le nom utilisateur doit contenir au moins 3 caracteres')
    .max(30, 'Le nom utilisateur ne peut pas depasser 30 caracteres')
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      'Le nom utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores'
    ),
  bio: z.string().max(500, 'La bio ne peut pas depasser 500 caracteres').optional(),
  github_url: z
    .string()
    .url('URL invalide')
    .regex(/github\.com/, 'Doit etre une URL GitHub')
    .optional()
    .or(z.literal('')),
  portfolio_url: z.string().url('URL invalide').optional().or(z.literal('')),
  avatar_url: z.string().url('URL invalide').optional().or(z.literal('')),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

interface ProfileEditFormProps {
  user: User;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const ProfileEditForm = ({ user, onSuccess, onCancel }: ProfileEditFormProps) => {
  const queryClient = useQueryClient();
  const { setUser } = useAuthStore();

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      username: user.username,
      bio: user.bio || '',
      github_url: user.github_url || '',
      portfolio_url: user.portfolio_url || '',
      avatar_url: user.avatar_url || '',
    },
  });

  const mutation = useMutation({
    mutationFn: (data: ProfileFormValues) => {
      const cleanData = {
        ...data,
        bio: data.bio || undefined,
        github_url: data.github_url || undefined,
        portfolio_url: data.portfolio_url || undefined,
        avatar_url: data.avatar_url || undefined,
      };
      return authApi.updateProfile(cleanData);
    },
    onSuccess: (updatedUser) => {
      setUser(updatedUser);
      queryClient.invalidateQueries({ queryKey: ['user'] });
      onSuccess?.();
    },
  });

  const onSubmit = (values: ProfileFormValues) => {
    mutation.mutate(values);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nom utilisateur</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="bio"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bio</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Parlez-nous de vous..."
                  className="resize-none"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                {(field.value?.length || 0)}/500 caracteres
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="avatar_url"
          render={({ field }) => (
            <FormItem>
              <FormLabel>URL Avatar</FormLabel>
              <FormControl>
                <Input placeholder="https://example.com/avatar.jpg" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="github_url"
          render={({ field }) => (
            <FormItem>
              <FormLabel>GitHub</FormLabel>
              <FormControl>
                <Input placeholder="https://github.com/username" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="portfolio_url"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Portfolio</FormLabel>
              <FormControl>
                <Input placeholder="https://votresite.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {mutation.error && (
          <p className="text-sm text-destructive">
            Une erreur est survenue lors de la mise a jour du profil
          </p>
        )}

        <div className="flex gap-3 pt-2">
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Sauvegarde...' : 'Sauvegarder'}
          </Button>
          {onCancel && (
            <Button type="button" variant="outline" onClick={onCancel}>
              Annuler
            </Button>
          )}
        </div>
      </form>
    </Form>
  );
};
