'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Save, X } from 'lucide-react';
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

  const inputClassName = "bg-anthracite-800/50 border-violet-500/20 text-violet-100 placeholder:text-violet-300/40 focus:border-violet-500/50 focus:ring-violet-500/20";
  const labelClassName = "text-violet-200";

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel className={labelClassName}>Nom utilisateur</FormLabel>
              <FormControl>
                <Input className={inputClassName} {...field} />
              </FormControl>
              <FormMessage className="text-red-400" />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="bio"
          render={({ field }) => (
            <FormItem>
              <FormLabel className={labelClassName}>Bio</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Parlez-nous de vous..."
                  className={`${inputClassName} resize-none min-h-[100px]`}
                  {...field}
                />
              </FormControl>
              <FormDescription className="text-violet-300/50">
                {(field.value?.length || 0)}/500 caracteres
              </FormDescription>
              <FormMessage className="text-red-400" />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="avatar_url"
          render={({ field }) => (
            <FormItem>
              <FormLabel className={labelClassName}>URL Avatar</FormLabel>
              <FormControl>
                <Input
                  placeholder="https://example.com/avatar.jpg"
                  className={inputClassName}
                  {...field}
                />
              </FormControl>
              <FormMessage className="text-red-400" />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="github_url"
          render={({ field }) => (
            <FormItem>
              <FormLabel className={labelClassName}>GitHub</FormLabel>
              <FormControl>
                <Input
                  placeholder="https://github.com/username"
                  className={inputClassName}
                  {...field}
                />
              </FormControl>
              <FormMessage className="text-red-400" />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="portfolio_url"
          render={({ field }) => (
            <FormItem>
              <FormLabel className={labelClassName}>Portfolio</FormLabel>
              <FormControl>
                <Input
                  placeholder="https://votresite.com"
                  className={inputClassName}
                  {...field}
                />
              </FormControl>
              <FormMessage className="text-red-400" />
            </FormItem>
          )}
        />

        {mutation.error && (
          <div className="p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-red-400 text-sm">
            Une erreur est survenue lors de la mise a jour du profil
          </div>
        )}

        <div className="flex gap-3 pt-4">
          <Button
            type="submit"
            disabled={mutation.isPending}
            className="bg-violet-600 hover:bg-violet-500 text-white gap-2"
          >
            <Save className="w-4 h-4" />
            {mutation.isPending ? 'Sauvegarde...' : 'Sauvegarder'}
          </Button>
          {onCancel && (
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              className="border-violet-500/30 text-violet-300 hover:bg-violet-500/20 hover:text-violet-100 gap-2"
            >
              <X className="w-4 h-4" />
              Annuler
            </Button>
          )}
        </div>
      </form>
    </Form>
  );
};
