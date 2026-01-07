'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, User, Shield, LogOut, Mail, CheckCircle, XCircle, Save, Github, Globe, Camera, Tags, Plus, Trash2, RefreshCw, Sparkles } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AuthGuard } from '@/components/auth';
import { useCurrentUser } from '@/hooks/use-current-user';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import { authApi, userKeywordsApi, personalizedApi } from '@/lib/api-client';
import { useAuthStore } from '@/store/auth-store';
import { useToast } from '@/hooks/use-toast';
import type { UserKeyword } from '@/types/auth';

const profileSchema = z.object({
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(30, 'Username cannot exceed 30 characters')
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      'Only letters, numbers, dashes and underscores'
    ),
  bio: z.string().max(500, 'Bio cannot exceed 500 characters').optional(),
  github_url: z
    .string()
    .url('Invalid URL')
    .regex(/github\.com/, 'Must be a GitHub URL')
    .optional()
    .or(z.literal('')),
  portfolio_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  avatar_url: z.string().url('Invalid URL').optional().or(z.literal('')),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

function KeywordsTab() {
  const [newKeyword, setNewKeyword] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const [newWeight, setNewWeight] = useState(1);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Fetch keywords
  const { data: keywordsData, isLoading: keywordsLoading } = useQuery({
    queryKey: ['user-keywords'],
    queryFn: userKeywordsApi.list,
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['personalized-stats'],
    queryFn: personalizedApi.getStats,
  });

  const keywords = keywordsData?.data || [];

  // Add keyword mutation
  const addMutation = useMutation({
    mutationFn: (data: { keyword: string; category?: string; weight?: number }) =>
      userKeywordsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-keywords'] });
      queryClient.invalidateQueries({ queryKey: ['personalized-stats'] });
      setNewKeyword('');
      setNewCategory('');
      setNewWeight(1);
      toast({ title: 'Keyword added', description: 'The keyword has been added successfully' });
    },
    onError: (error: Error) => {
      toast({ title: 'Error', description: error.message || 'Unable to add keyword', variant: 'destructive' });
    },
  });

  // Update keyword mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<UserKeyword> }) =>
      userKeywordsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-keywords'] });
    },
  });

  // Delete keyword mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => userKeywordsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-keywords'] });
      queryClient.invalidateQueries({ queryKey: ['personalized-stats'] });
    },
  });

  // Rescore mutation
  const rescoreMutation = useMutation({
    mutationFn: userKeywordsApi.rescore,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['personalized-stats'] });
      toast({ title: 'Rescoring started', description: 'Articles will be rescored in the background' });
    },
    onError: (error: Error) => {
      toast({ title: 'Error', description: error.message || 'Unable to start rescoring', variant: 'destructive' });
    },
  });

  const handleAddKeyword = (e: React.FormEvent) => {
    e.preventDefault();
    if (newKeyword.trim().length < 2) return;
    addMutation.mutate({
      keyword: newKeyword.trim(),
      category: newCategory.trim() || undefined,
      weight: newWeight,
    });
  };

  const handleToggleActive = (keyword: UserKeyword) => {
    updateMutation.mutate({
      id: keyword.id,
      data: { is_active: !keyword.is_active },
    });
  };

  const handleWeightChange = (keyword: UserKeyword, weight: number) => {
    updateMutation.mutate({
      id: keyword.id,
      data: { weight },
    });
  };

  const inputClassName = "bg-anthracite-800 border-violet-500/30 text-white placeholder:text-violet-300/50 focus:border-violet-500 focus:ring-violet-500/30";

  return (
    <TabsContent value="keywords" className="space-y-6">
      {/* Stats Card */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-lg border border-violet-500/20 bg-anthracite-900/50 p-4">
            <p className="text-xs text-violet-300/60 uppercase tracking-wide">Keywords</p>
            <p className="text-2xl font-bold text-violet-100 mt-1">{stats.keyword_count}</p>
          </div>
          <div className="rounded-lg border border-violet-500/20 bg-anthracite-900/50 p-4">
            <p className="text-xs text-violet-300/60 uppercase tracking-wide">Scored Articles</p>
            <p className="text-2xl font-bold text-violet-100 mt-1">{stats.scored_articles}</p>
          </div>
          <div className="rounded-lg border border-violet-500/20 bg-anthracite-900/50 p-4">
            <p className="text-xs text-violet-300/60 uppercase tracking-wide">Average Score</p>
            <p className="text-2xl font-bold text-violet-100 mt-1">{stats.average_score}</p>
          </div>
          <div className="rounded-lg border border-violet-500/20 bg-anthracite-900/50 p-4">
            <p className="text-xs text-violet-300/60 uppercase tracking-wide">High Relevance</p>
            <p className="text-2xl font-bold text-green-400 mt-1">{stats.high_relevance_count}</p>
          </div>
        </div>
      )}

      {/* Add Keyword Form */}
      <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur">
        <div className="p-6 border-b border-violet-500/10">
          <h2 className="text-lg font-semibold text-violet-100 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-violet-400" />
            Personalized Scoring
          </h2>
          <p className="text-sm text-violet-300/60 mt-1">
            Add keywords to personalize the relevance score of articles
          </p>
        </div>
        <form onSubmit={handleAddKeyword} className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="text-sm font-semibold text-white mb-2 block">Keyword</label>
              <Input
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                placeholder="e.g., React, TypeScript, AI..."
                className={inputClassName}
              />
            </div>
            <div className="w-full md:w-40">
              <label className="text-sm font-semibold text-white mb-2 block">Category (optional)</label>
              <Input
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                placeholder="e.g., Frontend"
                className={inputClassName}
              />
            </div>
            <div className="w-full md:w-32">
              <label className="text-sm font-semibold text-white mb-2 block">Weight: {newWeight.toFixed(1)}</label>
              <Slider
                value={[newWeight]}
                onValueChange={(v) => setNewWeight(v[0])}
                min={0.1}
                max={5}
                step={0.1}
                className="mt-3"
              />
            </div>
            <div className="flex items-end">
              <Button
                type="submit"
                disabled={addMutation.isPending || newKeyword.trim().length < 2}
                className="bg-violet-600 hover:bg-violet-500 text-white gap-2"
              >
                <Plus className="w-4 h-4" />
                Add
              </Button>
            </div>
          </div>
        </form>
      </div>

      {/* Keywords List */}
      <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur">
        <div className="p-6 border-b border-violet-500/10 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-violet-100">My Keywords</h2>
            <p className="text-sm text-violet-300/60 mt-1">
              {keywords.length} keyword{keywords.length !== 1 ? 's' : ''} configured
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => rescoreMutation.mutate()}
            disabled={rescoreMutation.isPending}
            className="gap-2 border-violet-500/30 text-violet-300 hover:bg-violet-500/20"
          >
            <RefreshCw className={`w-4 h-4 ${rescoreMutation.isPending ? 'animate-spin' : ''}`} />
            Rescore Articles
          </Button>
        </div>
        <div className="p-6">
          {keywordsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 bg-violet-500/10 rounded animate-pulse" />
              ))}
            </div>
          ) : keywords.length === 0 ? (
            <div className="text-center py-8 text-violet-300/60">
              <Tags className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No keywords configured</p>
              <p className="text-sm mt-1">Add keywords to personalize your feed</p>
            </div>
          ) : (
            <div className="space-y-3">
              {keywords.map((keyword) => (
                <div
                  key={keyword.id}
                  className={`flex items-center justify-between p-4 rounded-lg border ${
                    keyword.is_active
                      ? 'border-violet-500/30 bg-violet-500/5'
                      : 'border-violet-500/10 bg-anthracite-800/30 opacity-60'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <Switch
                      checked={keyword.is_active}
                      onCheckedChange={() => handleToggleActive(keyword)}
                    />
                    <div>
                      <p className="font-medium text-violet-100">{keyword.keyword}</p>
                      {keyword.category && (
                        <Badge variant="secondary" className="mt-1 bg-violet-500/20 text-violet-300 text-xs">
                          {keyword.category}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-24">
                      <p className="text-xs font-semibold text-white mb-1">Weight: {keyword.weight.toFixed(1)}</p>
                      <Slider
                        value={[keyword.weight]}
                        onValueChange={(v) => handleWeightChange(keyword, v[0])}
                        min={0.1}
                        max={5}
                        step={0.1}
                        disabled={!keyword.is_active}
                      />
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteMutation.mutate(keyword.id)}
                      disabled={deleteMutation.isPending}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/20"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Help text */}
      <div className="rounded-lg border border-violet-500/10 bg-anthracite-900/30 p-4">
        <p className="text-sm text-violet-300/60">
          <strong className="text-violet-300">How does it work?</strong> Articles are scored based on your keywords.
          The higher the weight, the higher articles containing that keyword will score.
          Use the <strong className="text-violet-300">For You</strong> feed to see articles sorted by relevance.
        </p>
      </div>
    </TabsContent>
  );
}

export default function ProfilePage() {
  const { user, isLoading } = useCurrentUser();
  const { logout, isLoggingOut } = useAuth();
  const [successMessage, setSuccessMessage] = useState('');
  const queryClient = useQueryClient();
  const { setUser } = useAuthStore();

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      username: user?.username || '',
      bio: user?.bio || '',
      github_url: user?.github_url || '',
      portfolio_url: user?.portfolio_url || '',
      avatar_url: user?.avatar_url || '',
    },
  });

  // Update form when user data loads
  if (user && !form.formState.isDirty && form.getValues('username') !== user.username) {
    form.reset({
      username: user.username || '',
      bio: user.bio || '',
      github_url: user.github_url || '',
      portfolio_url: user.portfolio_url || '',
      avatar_url: user.avatar_url || '',
    });
  }

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
      setSuccessMessage('Profile updated');
      setTimeout(() => setSuccessMessage(''), 3000);
    },
  });

  const onSubmit = (values: ProfileFormValues) => {
    mutation.mutate(values);
  };

  const userInitials = user?.username?.slice(0, 2).toUpperCase() || 'U';
  const watchedAvatar = form.watch('avatar_url');

  const inputClassName = "bg-anthracite-800/50 border-violet-500/20 text-violet-100 placeholder:text-violet-300/40 focus:border-violet-500/50 focus:ring-violet-500/20";
  const labelClassName = "text-violet-200 text-sm";

  return (
    <AuthGuard>
      <main className="min-h-screen bg-anthracite-950">
        {/* Header sticky */}
        <div className="sticky top-0 z-40 border-b border-violet-500/20 bg-anthracite-900/95 backdrop-blur supports-[backdrop-filter]:bg-anthracite-900/80">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link href="/">
                  <Button variant="ghost" size="sm" className="gap-2 text-violet-300 hover:text-violet-200 hover:bg-violet-500/20">
                    <ArrowLeft className="w-4 h-4" />
                    Home
                  </Button>
                </Link>
                <h1 className="text-2xl font-bold text-gradient-violet">
                  My Account
                </h1>
              </div>
              {user && (
                <div className="flex items-center gap-2">
                  {user.is_admin && (
                    <Badge className="bg-violet-500/20 text-violet-300 border-violet-500/30">Admin</Badge>
                  )}
                  {user.is_verified && (
                    <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Verified</Badge>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Success message */}
        {successMessage && (
          <div className="container mx-auto px-4 pt-4 max-w-4xl">
            <div className="p-3 rounded-lg border border-green-500/30 bg-green-500/10 text-green-400 text-sm flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              {successMessage}
            </div>
          </div>
        )}

        {/* Content */}
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <Tabs defaultValue="profile" className="space-y-6">
            <TabsList className="bg-anthracite-800/50 border border-violet-500/20 p-1">
              <TabsTrigger
                value="profile"
                className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-violet-100 text-violet-300/70"
              >
                <User className="w-4 h-4 mr-2" />
                Profile
              </TabsTrigger>
              <TabsTrigger
                value="keywords"
                className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-violet-100 text-violet-300/70"
              >
                <Tags className="w-4 h-4 mr-2" />
                Keywords
              </TabsTrigger>
              <TabsTrigger
                value="account"
                className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-violet-100 text-violet-300/70"
              >
                <Shield className="w-4 h-4 mr-2" />
                Account
              </TabsTrigger>
            </TabsList>

            {/* Profile Tab - Direct Edit */}
            <TabsContent value="profile">
              {isLoading ? (
                <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur p-6">
                  <div className="space-y-4">
                    <div className="h-24 w-24 rounded-full bg-violet-500/20 animate-pulse mx-auto" />
                    <div className="h-10 w-full bg-violet-500/10 rounded animate-pulse" />
                    <div className="h-24 w-full bg-violet-500/10 rounded animate-pulse" />
                  </div>
                </div>
              ) : user ? (
                <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur overflow-hidden">
                  {/* Avatar Section */}
                  <div className="p-6 border-b border-violet-500/10 flex flex-col items-center">
                    <div className="relative group">
                      <Avatar className="h-24 w-24 border-4 border-anthracite-800 ring-2 ring-violet-500/30">
                        <AvatarImage src={watchedAvatar || user.avatar_url} />
                        <AvatarFallback className="text-2xl bg-violet-500/20 text-violet-200">
                          {userInitials}
                        </AvatarFallback>
                      </Avatar>
                      <div className="absolute inset-0 rounded-full bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <Camera className="w-6 h-6 text-white" />
                      </div>
                    </div>
                    <p className="text-violet-300/60 text-sm mt-3">@{user.username}</p>
                  </div>

                  {/* Edit Form */}
                  <div className="p-6">
                    <Form {...form}>
                      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                          <FormField
                            control={form.control}
                            name="username"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className={labelClassName}>Username</FormLabel>
                                <FormControl>
                                  <Input className={inputClassName} {...field} />
                                </FormControl>
                                <FormMessage className="text-red-400 text-xs" />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={form.control}
                            name="avatar_url"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className={labelClassName}>Avatar URL</FormLabel>
                                <FormControl>
                                  <Input
                                    placeholder="https://example.com/avatar.jpg"
                                    className={inputClassName}
                                    {...field}
                                  />
                                </FormControl>
                                <FormMessage className="text-red-400 text-xs" />
                              </FormItem>
                            )}
                          />
                        </div>

                        <FormField
                          control={form.control}
                          name="bio"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className={labelClassName}>Bio</FormLabel>
                              <FormControl>
                                <Textarea
                                  placeholder="Tell us about yourself..."
                                  className={`${inputClassName} resize-none min-h-[100px]`}
                                  {...field}
                                />
                              </FormControl>
                              <FormDescription className="text-violet-300/50 text-xs">
                                {(field.value?.length || 0)}/500 characters
                              </FormDescription>
                              <FormMessage className="text-red-400 text-xs" />
                            </FormItem>
                          )}
                        />

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                          <FormField
                            control={form.control}
                            name="github_url"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className={labelClassName}>
                                  <Github className="w-4 h-4 inline mr-1" />
                                  GitHub
                                </FormLabel>
                                <FormControl>
                                  <Input
                                    placeholder="https://github.com/username"
                                    className={inputClassName}
                                    {...field}
                                  />
                                </FormControl>
                                <FormMessage className="text-red-400 text-xs" />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={form.control}
                            name="portfolio_url"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className={labelClassName}>
                                  <Globe className="w-4 h-4 inline mr-1" />
                                  Portfolio
                                </FormLabel>
                                <FormControl>
                                  <Input
                                    placeholder="https://yoursite.com"
                                    className={inputClassName}
                                    {...field}
                                  />
                                </FormControl>
                                <FormMessage className="text-red-400 text-xs" />
                              </FormItem>
                            )}
                          />
                        </div>

                        {mutation.error && (
                          <div className="p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-red-400 text-sm">
                            An error occurred while updating
                          </div>
                        )}

                        <div className="flex justify-end pt-2">
                          <Button
                            type="submit"
                            disabled={mutation.isPending || !form.formState.isDirty}
                            className="bg-violet-600 hover:bg-violet-500 text-white gap-2"
                          >
                            <Save className="w-4 h-4" />
                            {mutation.isPending ? 'Saving...' : 'Save'}
                          </Button>
                        </div>
                      </form>
                    </Form>
                  </div>
                </div>
              ) : null}
            </TabsContent>

            {/* Keywords Tab */}
            <KeywordsTab />

            {/* Account Tab */}
            <TabsContent value="account" className="space-y-6">
              {/* Account Info */}
              <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur">
                <div className="p-6 border-b border-violet-500/10">
                  <h2 className="text-lg font-semibold text-violet-100">Account Information</h2>
                  <p className="text-sm text-violet-300/60 mt-1">Your ZenWatch account details</p>
                </div>
                <div className="p-6 space-y-4">
                  {isLoading ? (
                    <div className="space-y-3">
                      <div className="h-4 w-48 bg-violet-500/10 rounded animate-pulse" />
                      <div className="h-4 w-64 bg-violet-500/10 rounded animate-pulse" />
                    </div>
                  ) : user ? (
                    <>
                      <div className="flex items-center justify-between py-3 border-b border-violet-500/10">
                        <div className="flex items-center gap-3">
                          <Mail className="w-5 h-5 text-violet-400" />
                          <div>
                            <p className="text-sm font-medium text-violet-100">Email</p>
                            <p className="text-sm text-violet-300/60">{user.email}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between py-3 border-b border-violet-500/10">
                        <div className="flex items-center gap-3">
                          <Shield className="w-5 h-5 text-violet-400" />
                          <div>
                            <p className="text-sm font-medium text-violet-100">Role</p>
                            <p className="text-sm text-violet-300/60 capitalize">{user.role || 'User'}</p>
                          </div>
                        </div>
                        {user.is_admin && (
                          <Badge className="bg-violet-500/20 text-violet-300 border-violet-500/30">Admin</Badge>
                        )}
                      </div>
                      <div className="flex items-center justify-between py-3">
                        <div className="flex items-center gap-3">
                          {user.is_verified ? (
                            <CheckCircle className="w-5 h-5 text-green-400" />
                          ) : (
                            <XCircle className="w-5 h-5 text-orange-400" />
                          )}
                          <div>
                            <p className="text-sm font-medium text-violet-100">Verification</p>
                            <p className="text-sm text-violet-300/60">
                              {user.is_verified ? 'Account verified' : 'Account not verified'}
                            </p>
                          </div>
                        </div>
                        {user.is_verified ? (
                          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Verified</Badge>
                        ) : (
                          <Badge variant="outline" className="text-orange-400 border-orange-500/30">Pending</Badge>
                        )}
                      </div>
                    </>
                  ) : null}
                </div>
              </div>

              {/* Danger Zone */}
              <div className="rounded-xl border border-red-500/30 bg-anthracite-900/50 backdrop-blur">
                <div className="p-6 border-b border-red-500/20">
                  <h2 className="text-lg font-semibold text-red-400">Danger Zone</h2>
                  <p className="text-sm text-red-400/60 mt-1">Irreversible actions</p>
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-violet-100">Log out</p>
                      <p className="text-sm text-violet-300/60">
                        Sign out from ZenWatch
                      </p>
                    </div>
                    <Button
                      variant="destructive"
                      onClick={logout}
                      disabled={isLoggingOut}
                      className="gap-2"
                    >
                      <LogOut className="w-4 h-4" />
                      {isLoggingOut ? 'Logging out...' : 'Log out'}
                    </Button>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </AuthGuard>
  );
}
