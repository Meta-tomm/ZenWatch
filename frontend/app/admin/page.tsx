'use client';

import { useState } from 'react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import {
  ArrowLeft,
  Users,
  Activity,
  Database,
  Tag,
  RefreshCw,
  Play,
  CheckCircle,
  XCircle,
  Clock,
  Trash2,
  Shield,
  Search,
  Youtube,
  Zap,
  TrendingUp,
  FileText,
  Settings,
} from 'lucide-react';
import { AdminGuard } from '@/components/admin/AdminGuard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  useAdminUsers,
  useUpdateUser,
  useDeleteUser,
  useScrapingHistory,
  useScrapingStats,
  useTriggerScraping,
  useTriggerYouTubeScraping,
  useTriggerRescore,
  useAdminKeywords,
  useCreateKeyword,
  useDeleteKeyword,
  useAdminSources,
  useUpdateSource,
} from '@/hooks/use-admin';
import type { AdminUser, ScrapingRun } from '@/types/admin';
import type { Source } from '@/types';

// Stats Card Component
function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  color = 'violet',
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  trend?: string;
  color?: 'violet' | 'green' | 'red' | 'blue';
}) {
  const colors = {
    violet: 'from-violet-500/20 to-violet-600/10 border-violet-500/30 text-violet-400',
    green: 'from-green-500/20 to-green-600/10 border-green-500/30 text-green-400',
    red: 'from-red-500/20 to-red-600/10 border-red-500/30 text-red-400',
    blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30 text-blue-400',
  };

  return (
    <div className={`rounded-xl border bg-gradient-to-br ${colors[color]} p-4`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-violet-300/70">{title}</p>
          <p className="text-2xl font-bold text-violet-100 mt-1">{value}</p>
          {trend && <p className="text-xs text-violet-300/50 mt-1">{trend}</p>}
        </div>
        <Icon className="w-10 h-10 opacity-50" />
      </div>
    </div>
  );
}

// Status Badge for scraping runs
function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, { icon: React.ElementType; className: string }> = {
    success: { icon: CheckCircle, className: 'bg-green-500/20 text-green-400 border-green-500/30' },
    failed: { icon: XCircle, className: 'bg-red-500/20 text-red-400 border-red-500/30' },
    running: { icon: RefreshCw, className: 'bg-blue-500/20 text-blue-400 border-blue-500/30 animate-pulse' },
    pending: { icon: Clock, className: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
  };

  const variant = variants[status] || variants.pending;
  const Icon = variant.icon;

  return (
    <Badge className={variant.className}>
      <Icon className="w-3 h-3 mr-1" />
      {status}
    </Badge>
  );
}

// Dashboard Tab Content
function DashboardTab() {
  const { data: scrapingStats } = useScrapingStats();
  const { data: users } = useAdminUsers({ limit: 1 });
  const { data: scrapingHistory } = useScrapingHistory(5);

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Users"
          value={users?.total || 0}
          icon={Users}
          color="violet"
        />
        <StatCard
          title="Scraping Runs"
          value={scrapingStats?.total_runs || 0}
          icon={Activity}
          trend={`${scrapingStats?.success_rate || 0}% success rate`}
          color="blue"
        />
        <StatCard
          title="Articles Scraped"
          value={scrapingStats?.total_articles_scraped || 0}
          icon={FileText}
          color="green"
        />
        <StatCard
          title="Articles Saved"
          value={scrapingStats?.total_articles_saved || 0}
          icon={Database}
          color="violet"
        />
      </div>

      {/* Recent Scraping Activity */}
      <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur">
        <div className="p-4 border-b border-violet-500/10 flex items-center justify-between">
          <h2 className="font-semibold text-violet-100">Recent Activity</h2>
          <Link href="/admin?tab=scraping">
            <Button variant="ghost" size="sm" className="text-violet-300 hover:text-violet-200">
              View all
            </Button>
          </Link>
        </div>
        <div className="p-4">
          {scrapingHistory && scrapingHistory.length > 0 ? (
            <div className="space-y-3">
              {scrapingHistory.map((run: ScrapingRun) => (
                <div
                  key={run.task_id}
                  className="flex items-center justify-between p-3 rounded-lg bg-anthracite-800/50 border border-violet-500/10"
                >
                  <div className="flex items-center gap-3">
                    <StatusBadge status={run.status} />
                    <div>
                      <p className="text-sm font-medium text-violet-100">{run.source_type}</p>
                      <p className="text-xs text-violet-300/50">
                        {formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-violet-100">{run.articles_saved} / {run.articles_scraped}</p>
                    <p className="text-xs text-violet-300/50">saved</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-violet-300/50 py-8">No recent activity</p>
          )}
        </div>
      </div>
    </div>
  );
}

// Users Tab Content
function UsersTab() {
  const [search, setSearch] = useState('');
  const { data: usersData, isLoading } = useAdminUsers({ search: search || undefined, limit: 50 });
  const updateUser = useUpdateUser();
  const deleteUser = useDeleteUser();

  const handleToggleAdmin = (user: AdminUser) => {
    updateUser.mutate({ userId: user.id, data: { is_admin: !user.is_admin } });
  };

  const handleToggleActive = (user: AdminUser) => {
    updateUser.mutate({ userId: user.id, data: { is_active: !user.is_active } });
  };

  const handleDelete = (userId: number) => {
    deleteUser.mutate(userId);
  };

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-violet-300/50" />
          <Input
            placeholder="Search user..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 bg-anthracite-800/50 border-violet-500/20 text-violet-100"
          />
        </div>
        <p className="text-sm text-violet-300/50">
          {usersData?.total || 0} users
        </p>
      </div>

      {/* Users Table */}
      <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-violet-500/10 hover:bg-transparent">
              <TableHead className="text-violet-300">User</TableHead>
              <TableHead className="text-violet-300">Email</TableHead>
              <TableHead className="text-violet-300">Status</TableHead>
              <TableHead className="text-violet-300">Admin</TableHead>
              <TableHead className="text-violet-300">Active</TableHead>
              <TableHead className="text-violet-300 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i} className="border-violet-500/10">
                  <TableCell><Skeleton className="h-8 w-32 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-40 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-16 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-10 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-10 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-8 w-8 bg-violet-500/10 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : usersData?.data.map((user) => (
              <TableRow key={user.id} className="border-violet-500/10 hover:bg-violet-500/5">
                <TableCell>
                  <div className="flex items-center gap-3">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user.avatar_url} />
                      <AvatarFallback className="bg-violet-500/20 text-violet-200 text-xs">
                        {user.username?.slice(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <span className="font-medium text-violet-100">{user.username}</span>
                  </div>
                </TableCell>
                <TableCell className="text-violet-300/70">{user.email}</TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    {user.is_verified && (
                      <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                        Verified
                      </Badge>
                    )}
                    {!user.is_active && (
                      <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                        Disabled
                      </Badge>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <Switch
                    checked={user.is_admin}
                    onCheckedChange={() => handleToggleAdmin(user)}
                    disabled={updateUser.isPending}
                  />
                </TableCell>
                <TableCell>
                  <Switch
                    checked={user.is_active}
                    onCheckedChange={() => handleToggleActive(user)}
                    disabled={updateUser.isPending}
                  />
                </TableCell>
                <TableCell className="text-right">
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent className="bg-anthracite-900 border-violet-500/20">
                      <AlertDialogHeader>
                        <AlertDialogTitle className="text-violet-100">Delete user?</AlertDialogTitle>
                        <AlertDialogDescription className="text-violet-300/70">
                          This action is irreversible. User {user.username} will be permanently deleted.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel className="border-violet-500/20 text-violet-300 hover:bg-violet-500/10">
                          Cancel
                        </AlertDialogCancel>
                        <AlertDialogAction
                          onClick={() => handleDelete(user.id)}
                          className="bg-red-600 hover:bg-red-500"
                        >
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

// Sources Tab Content
function SourcesTab() {
  const { data: sources, isLoading } = useAdminSources();
  const updateSource = useUpdateSource();

  const handleToggleSource = (source: Source) => {
    updateSource.mutate({ id: source.id, data: { is_active: !source.is_active } });
  };

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-violet-500/10 hover:bg-transparent">
              <TableHead className="text-violet-300">Source</TableHead>
              <TableHead className="text-violet-300">Type</TableHead>
              <TableHead className="text-violet-300">Frequency</TableHead>
              <TableHead className="text-violet-300">Last Scrape</TableHead>
              <TableHead className="text-violet-300">Active</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <TableRow key={i} className="border-violet-500/10">
                  <TableCell><Skeleton className="h-4 w-24 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-28 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-10 bg-violet-500/10" /></TableCell>
                </TableRow>
              ))
            ) : sources?.map((source) => (
              <TableRow key={source.id} className="border-violet-500/10 hover:bg-violet-500/5">
                <TableCell className="font-medium text-violet-100">{source.name}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="text-violet-300 border-violet-500/30">
                    {source.type}
                  </Badge>
                </TableCell>
                <TableCell className="text-violet-300/70">
                  Every {source.scrape_frequency_hours}h
                </TableCell>
                <TableCell className="text-violet-300/70">
                  {source.last_scraped_at
                    ? formatDistanceToNow(new Date(source.last_scraped_at), { addSuffix: true })
                    : 'Never'
                  }
                </TableCell>
                <TableCell>
                  <Switch
                    checked={source.is_active}
                    onCheckedChange={() => handleToggleSource(source)}
                    disabled={updateSource.isPending}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

// Keywords Tab Content
function KeywordsTab() {
  const [newKeyword, setNewKeyword] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const { data: keywords, isLoading } = useAdminKeywords();
  const createKeyword = useCreateKeyword();
  const deleteKeyword = useDeleteKeyword();

  const handleCreate = () => {
    if (newKeyword.trim()) {
      createKeyword.mutate({
        keyword: newKeyword.trim(),
        category: newCategory.trim() || 'general',
        weight: 1.0,
        is_active: true,
      });
      setNewKeyword('');
      setNewCategory('');
    }
  };

  const handleDelete = (id: string) => {
    deleteKeyword.mutate(id);
  };

  return (
    <div className="space-y-4">
      {/* Add Keyword Form */}
      <div className="flex items-center gap-4 p-4 rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur">
        <Input
          placeholder="New keyword..."
          value={newKeyword}
          onChange={(e) => setNewKeyword(e.target.value)}
          className="flex-1 bg-anthracite-800/50 border-violet-500/20 text-violet-100"
        />
        <Input
          placeholder="Category (optional)"
          value={newCategory}
          onChange={(e) => setNewCategory(e.target.value)}
          className="w-48 bg-anthracite-800/50 border-violet-500/20 text-violet-100"
        />
        <Button
          onClick={handleCreate}
          disabled={!newKeyword.trim() || createKeyword.isPending}
          className="bg-violet-600 hover:bg-violet-500"
        >
          Add
        </Button>
      </div>

      {/* Keywords List */}
      <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-violet-500/10 hover:bg-transparent">
              <TableHead className="text-violet-300">Keyword</TableHead>
              <TableHead className="text-violet-300">Category</TableHead>
              <TableHead className="text-violet-300">Weight</TableHead>
              <TableHead className="text-violet-300">Status</TableHead>
              <TableHead className="text-violet-300 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i} className="border-violet-500/10">
                  <TableCell><Skeleton className="h-4 w-24 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-12 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-16 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-8 w-8 bg-violet-500/10 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : keywords?.map((keyword) => (
              <TableRow key={keyword.id} className="border-violet-500/10 hover:bg-violet-500/5">
                <TableCell className="font-medium text-violet-100">{keyword.keyword}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="text-violet-300 border-violet-500/30">
                    {keyword.category}
                  </Badge>
                </TableCell>
                <TableCell className="text-violet-300/70">{keyword.weight}</TableCell>
                <TableCell>
                  {keyword.is_active ? (
                    <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Active</Badge>
                  ) : (
                    <Badge className="bg-red-500/20 text-red-400 border-red-500/30">Inactive</Badge>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(keyword.id)}
                    disabled={deleteKeyword.isPending}
                    className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

// Scraping Tab Content
function ScrapingTab() {
  const { data: history, isLoading, refetch } = useScrapingHistory(30);
  const { data: stats } = useScrapingStats();
  const triggerScraping = useTriggerScraping();
  const triggerYouTube = useTriggerYouTubeScraping();
  const triggerRescore = useTriggerRescore();

  const handleTriggerAll = () => {
    triggerScraping.mutate(undefined);
  };

  const handleTriggerYouTube = () => {
    triggerYouTube.mutate();
  };

  const handleRescore = () => {
    triggerRescore.mutate(false);
  };

  return (
    <div className="space-y-6">
      {/* Action Buttons */}
      <div className="flex flex-wrap items-center gap-3">
        <Button
          onClick={handleTriggerAll}
          disabled={triggerScraping.isPending}
          className="bg-violet-600 hover:bg-violet-500 gap-2"
        >
          {triggerScraping.isPending ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          Run Full Scraping
        </Button>
        <Button
          onClick={handleTriggerYouTube}
          disabled={triggerYouTube.isPending}
          variant="outline"
          className="border-violet-500/30 text-violet-300 hover:bg-violet-500/10 gap-2"
        >
          {triggerYouTube.isPending ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Youtube className="w-4 h-4" />
          )}
          Scrape YouTube
        </Button>
        <Button
          onClick={handleRescore}
          disabled={triggerRescore.isPending}
          variant="outline"
          className="border-violet-500/30 text-violet-300 hover:bg-violet-500/10 gap-2"
        >
          {triggerRescore.isPending ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Zap className="w-4 h-4" />
          )}
          Rescore Articles
        </Button>
        <Button
          onClick={() => refetch()}
          variant="ghost"
          className="text-violet-300 hover:text-violet-200 hover:bg-violet-500/10 gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </Button>
      </div>

      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            title="Total Runs"
            value={stats.total_runs}
            icon={Activity}
            color="violet"
          />
          <StatCard
            title="Successes"
            value={stats.successful_runs}
            icon={CheckCircle}
            color="green"
          />
          <StatCard
            title="Failures"
            value={stats.failed_runs}
            icon={XCircle}
            color="red"
          />
          <StatCard
            title="Success Rate"
            value={`${stats.success_rate}%`}
            icon={TrendingUp}
            color="blue"
          />
        </div>
      )}

      {/* History Table */}
      <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-violet-500/10 hover:bg-transparent">
              <TableHead className="text-violet-300">Status</TableHead>
              <TableHead className="text-violet-300">Source</TableHead>
              <TableHead className="text-violet-300">Scraped</TableHead>
              <TableHead className="text-violet-300">Saved</TableHead>
              <TableHead className="text-violet-300">Started</TableHead>
              <TableHead className="text-violet-300">Finished</TableHead>
              <TableHead className="text-violet-300">Error</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i} className="border-violet-500/10">
                  <TableCell><Skeleton className="h-6 w-20 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-12 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-12 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-28 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-28 bg-violet-500/10" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-32 bg-violet-500/10" /></TableCell>
                </TableRow>
              ))
            ) : history?.map((run: ScrapingRun) => (
              <TableRow key={run.task_id} className="border-violet-500/10 hover:bg-violet-500/5">
                <TableCell><StatusBadge status={run.status} /></TableCell>
                <TableCell className="font-medium text-violet-100">{run.source_type}</TableCell>
                <TableCell className="text-violet-300/70">{run.articles_scraped}</TableCell>
                <TableCell className="text-violet-300/70">{run.articles_saved}</TableCell>
                <TableCell className="text-violet-300/70 text-sm">
                  {formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}
                </TableCell>
                <TableCell className="text-violet-300/70 text-sm">
                  {run.completed_at
                    ? formatDistanceToNow(new Date(run.completed_at), { addSuffix: true })
                    : '-'
                  }
                </TableCell>
                <TableCell className="max-w-xs truncate text-red-400/70 text-sm">
                  {run.error_message || '-'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

// Main Admin Page
export default function AdminPage() {
  return (
    <AdminGuard>
      <main className="min-h-screen bg-anthracite-950">
        {/* Header */}
        <div className="sticky top-0 z-40 border-b border-violet-500/20 bg-anthracite-900/95 backdrop-blur supports-[backdrop-filter]:bg-anthracite-900/80">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="sm" className="gap-2 text-violet-300 hover:text-violet-200 hover:bg-violet-500/20">
                  <ArrowLeft className="w-4 h-4" />
                  Home
                </Button>
              </Link>
              <div className="flex items-center gap-2">
                <Shield className="w-6 h-6 text-violet-400" />
                <h1 className="text-2xl font-bold text-gradient-violet">
                  Administration
                </h1>
              </div>
              <Link href="/config">
                <Button variant="outline" size="sm" className="gap-2 border-violet-500/30 text-violet-300 hover:bg-violet-500/20">
                  <Settings className="w-4 h-4" />
                  Advanced Configuration
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="container mx-auto px-4 py-8">
          <Tabs defaultValue="dashboard" className="space-y-6">
            <TabsList className="bg-anthracite-800/50 border border-violet-500/20 p-1 flex-wrap">
              <TabsTrigger
                value="dashboard"
                className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-violet-100 text-violet-300/70"
              >
                <Activity className="w-4 h-4 mr-2" />
                Dashboard
              </TabsTrigger>
              <TabsTrigger
                value="users"
                className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-violet-100 text-violet-300/70"
              >
                <Users className="w-4 h-4 mr-2" />
                Users
              </TabsTrigger>
              <TabsTrigger
                value="sources"
                className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-violet-100 text-violet-300/70"
              >
                <Database className="w-4 h-4 mr-2" />
                Sources
              </TabsTrigger>
              <TabsTrigger
                value="keywords"
                className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-violet-100 text-violet-300/70"
              >
                <Tag className="w-4 h-4 mr-2" />
                Keywords
              </TabsTrigger>
              <TabsTrigger
                value="scraping"
                className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-violet-100 text-violet-300/70"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Scraping
              </TabsTrigger>
            </TabsList>

            <TabsContent value="dashboard">
              <DashboardTab />
            </TabsContent>

            <TabsContent value="users">
              <UsersTab />
            </TabsContent>

            <TabsContent value="sources">
              <SourcesTab />
            </TabsContent>

            <TabsContent value="keywords">
              <KeywordsTab />
            </TabsContent>

            <TabsContent value="scraping">
              <ScrapingTab />
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </AdminGuard>
  );
}
