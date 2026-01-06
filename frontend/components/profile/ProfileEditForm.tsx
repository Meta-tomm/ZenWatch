'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
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
import { useToast } from '@/hooks/use-toast';
import { usersApi } from '@/lib/api-client';
import { useAuthStore } from '@/store/auth-store';
import type { User } from '@/types/auth';

const profileSchema = z.object({
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(30, 'Username must be at most 30 characters')
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      'Username can only contain letters, numbers, underscores and hyphens'
    ),
  bio: z.string().max(500, 'Bio must be at most 500 characters').optional(),
  github_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  portfolio_url: z.string().url('Invalid URL').optional().or(z.literal('')),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

interface ProfileEditFormProps {
  user: User;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const ProfileEditForm = ({ user, onSuccess, onCancel }: ProfileEditFormProps) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { setUser } = useAuthStore();

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      username: user.username,
      bio: user.bio || '',
      github_url: user.github_url || '',
      portfolio_url: user.portfolio_url || '',
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: ProfileFormValues) => {
      // Clean empty strings to undefined
      const cleanData = {
        ...data,
        bio: data.bio || undefined,
        github_url: data.github_url || undefined,
        portfolio_url: data.portfolio_url || undefined,
      };
      return usersApi.updateProfile(cleanData);
    },
    onSuccess: (updatedUser) => {
      setUser(updatedUser);
      queryClient.invalidateQueries({ queryKey: ['user'] });
      toast({
        title: 'Profile updated',
        description: 'Your changes have been saved',
      });
      onSuccess?.();
    },
    onError: (error: Error) => {
      toast({
        title: 'Update failed',
        description: error.message || 'Could not update profile',
        variant: 'destructive',
      });
    },
  });

  const onSubmit = (data: ProfileFormValues) => {
    updateMutation.mutate(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-violet-200">Username</FormLabel>
              <FormControl>
                <Input
                  className="bg-anthracite-800 border-violet-500/30 text-violet-100"
                  {...field}
                />
              </FormControl>
              <FormDescription className="text-violet-300/60">
                Your public display name
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="bio"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-violet-200">Bio</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Tell us about yourself..."
                  className="bg-anthracite-800 border-violet-500/30 text-violet-100 min-h-[100px]"
                  {...field}
                />
              </FormControl>
              <FormDescription className="text-violet-300/60">
                {field.value?.length || 0}/500 characters
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="github_url"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-violet-200">GitHub URL</FormLabel>
              <FormControl>
                <Input
                  placeholder="https://github.com/username"
                  className="bg-anthracite-800 border-violet-500/30 text-violet-100"
                  {...field}
                />
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
              <FormLabel className="text-violet-200">Portfolio URL</FormLabel>
              <FormControl>
                <Input
                  placeholder="https://yourportfolio.com"
                  className="bg-anthracite-800 border-violet-500/30 text-violet-100"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex items-center justify-end gap-3 pt-4">
          {onCancel && (
            <Button
              type="button"
              variant="ghost"
              onClick={onCancel}
              disabled={updateMutation.isPending}
              className="text-violet-300/70 hover:text-violet-200"
            >
              Cancel
            </Button>
          )}
          <Button
            type="submit"
            disabled={updateMutation.isPending}
            className="bg-violet-600 hover:bg-violet-700 text-white"
          >
            {updateMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Changes'
            )}
          </Button>
        </div>
      </form>
    </Form>
  );
};
