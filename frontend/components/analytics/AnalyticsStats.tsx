'use client';

import { useEffect, useState } from 'react';
import { useAnalyticsSummary, useTopKeywords, useDailyStats } from '@/hooks/use-analytics';
import {
  FileText,
  Activity,
  TrendingUp,
  Clock,
  Database,
  Tag,
  RefreshCw,
  Zap,
  BarChart3,
  PieChart,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';

// Animated counter component
function AnimatedCounter({ value, duration = 1000 }: { value: number; duration?: number }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (value === 0) {
      setDisplayValue(0);
      return;
    }

    const startTime = Date.now();
    const startValue = displayValue;
    const diff = value - startValue;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const current = Math.round(startValue + diff * easeOutQuart);
      setDisplayValue(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  return <span>{displayValue.toLocaleString()}</span>;
}

// Large stat card for main metrics
function LargeStatCard({
  icon: Icon,
  label,
  value,
  subtitle,
  color = 'violet',
  isLoading = false,
}: {
  icon: React.ElementType;
  label: string;
  value: number;
  subtitle?: string;
  color?: 'violet' | 'green' | 'blue' | 'orange' | 'pink';
  isLoading?: boolean;
}) {
  const colors = {
    violet: 'from-violet-500/30 to-violet-600/10 border-violet-500/40 text-violet-400',
    green: 'from-green-500/30 to-green-600/10 border-green-500/40 text-green-400',
    blue: 'from-blue-500/30 to-blue-600/10 border-blue-500/40 text-blue-400',
    orange: 'from-orange-500/30 to-orange-600/10 border-orange-500/40 text-orange-400',
    pink: 'from-pink-500/30 to-pink-600/10 border-pink-500/40 text-pink-400',
  };

  if (isLoading) {
    return (
      <div className="p-6 rounded-xl bg-gradient-to-br from-violet-500/10 to-transparent border border-violet-500/20">
        <Skeleton className="h-10 w-10 rounded-lg bg-violet-500/20 mb-4" />
        <Skeleton className="h-4 w-20 bg-violet-500/10 mb-2" />
        <Skeleton className="h-8 w-24 bg-violet-500/20" />
      </div>
    );
  }

  return (
    <div className={`p-6 rounded-xl bg-gradient-to-br ${colors[color]} border transition-all hover:scale-[1.02]`}>
      <div className={`p-3 rounded-lg bg-gradient-to-br ${colors[color]} w-fit mb-4`}>
        <Icon className="w-6 h-6" />
      </div>
      <p className="text-sm text-violet-300/70 mb-1">{label}</p>
      <p className="text-3xl font-bold text-violet-100">
        <AnimatedCounter value={value} />
      </p>
      {subtitle && <p className="text-xs text-violet-300/50 mt-1">{subtitle}</p>}
    </div>
  );
}

// Mini bar chart for daily stats
function MiniBarChart({ data }: { data: { date: string; count: number }[] }) {
  const maxCount = Math.max(...data.map(d => d.count), 1);

  return (
    <div className="flex items-end gap-1 h-16">
      {data.map((item, idx) => (
        <div key={idx} className="flex-1 flex flex-col items-center gap-1">
          <div
            className="w-full bg-violet-500/40 rounded-t transition-all hover:bg-violet-500/60"
            style={{ height: `${(item.count / maxCount) * 100}%`, minHeight: '4px' }}
          />
          <span className="text-[10px] text-violet-300/40">
            {new Date(item.date).toLocaleDateString('fr-FR', { weekday: 'short' }).slice(0, 2)}
          </span>
        </div>
      ))}
    </div>
  );
}

// Category distribution bar
function CategoryBar({ categories }: { categories: Record<string, number> }) {
  const total = Object.values(categories).reduce((a, b) => a + b, 0);
  if (total === 0) return null;

  const colors = [
    'bg-violet-500',
    'bg-blue-500',
    'bg-green-500',
    'bg-orange-500',
    'bg-pink-500',
    'bg-cyan-500',
  ];

  const sortedCategories = Object.entries(categories)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 6);

  return (
    <div className="space-y-3">
      <div className="flex h-3 rounded-full overflow-hidden bg-anthracite-800">
        {sortedCategories.map(([category, count], idx) => (
          <div
            key={category}
            className={`${colors[idx % colors.length]} transition-all`}
            style={{ width: `${(count / total) * 100}%` }}
            title={`${category}: ${count}`}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {sortedCategories.map(([category, count], idx) => (
          <div key={category} className="flex items-center gap-1.5 text-xs">
            <div className={`w-2 h-2 rounded-full ${colors[idx % colors.length]}`} />
            <span className="text-violet-300/70 capitalize">{category}</span>
            <span className="text-violet-300/40">({Math.round((count / total) * 100)}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AnalyticsStats() {
  const { data: summary, isLoading: summaryLoading, dataUpdatedAt } = useAnalyticsSummary();
  const { data: topKeywords, isLoading: keywordsLoading } = useTopKeywords(7, 8);
  const { data: dailyStats, isLoading: dailyLoading } = useDailyStats(7);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    if (dataUpdatedAt) {
      const updateTime = new Date(dataUpdatedAt);
      setLastUpdate(updateTime.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    }
  }, [dataUpdatedAt]);

  const isLoading = summaryLoading;

  // Prepare daily chart data
  const chartData = dailyStats?.slice(0, 7).reverse().map((d: any) => ({
    date: d.date,
    count: d.total_articles,
  })) || [];

  return (
    <div className="border-b border-violet-500/20 bg-anthracite-900/80 backdrop-blur">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Activity className="w-6 h-6 text-violet-400" />
            <h2 className="text-lg font-semibold text-violet-200">Statistiques en temps reel</h2>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/20 border border-green-500/30">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs font-medium text-green-400">Live</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-violet-300/50">
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Derniere MAJ: {lastUpdate || '--:--:--'}</span>
          </div>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
          <LargeStatCard
            icon={FileText}
            label="Articles totaux"
            value={summary?.total_articles || 0}
            color="violet"
            isLoading={isLoading}
          />
          <LargeStatCard
            icon={Clock}
            label="Scraped aujourd'hui"
            value={summary?.articles_scraped_today || 0}
            subtitle="Nouveaux articles"
            color="green"
            isLoading={isLoading}
          />
          <LargeStatCard
            icon={TrendingUp}
            label="Score moyen"
            value={Math.round(summary?.avg_score_last_7_days || 0)}
            subtitle="7 derniers jours"
            color="blue"
            isLoading={isLoading}
          />
          <LargeStatCard
            icon={Database}
            label="Sources actives"
            value={summary?.total_sources || 0}
            color="orange"
            isLoading={isLoading}
          />
          <LargeStatCard
            icon={Tag}
            label="Keywords actifs"
            value={summary?.total_keywords || 0}
            color="pink"
            isLoading={isLoading}
          />
        </div>

        {/* Secondary Row: Chart + Categories + Keywords */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Daily Activity Chart */}
          <div className="p-4 rounded-xl bg-anthracite-800/50 border border-violet-500/20">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-4 h-4 text-violet-400" />
              <span className="text-sm font-medium text-violet-200">Activite (7 jours)</span>
            </div>
            {dailyLoading ? (
              <Skeleton className="h-16 w-full bg-violet-500/10" />
            ) : (
              <MiniBarChart data={chartData} />
            )}
          </div>

          {/* Category Distribution */}
          <div className="p-4 rounded-xl bg-anthracite-800/50 border border-violet-500/20">
            <div className="flex items-center gap-2 mb-4">
              <PieChart className="w-4 h-4 text-violet-400" />
              <span className="text-sm font-medium text-violet-200">Repartition par categorie</span>
            </div>
            {isLoading ? (
              <Skeleton className="h-16 w-full bg-violet-500/10" />
            ) : (
              <CategoryBar categories={summary?.articles_by_category || {}} />
            )}
          </div>

          {/* Top Keywords */}
          <div className="p-4 rounded-xl bg-anthracite-800/50 border border-violet-500/20">
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-4 h-4 text-violet-400" />
              <span className="text-sm font-medium text-violet-200">Top Keywords</span>
            </div>
            {keywordsLoading ? (
              <div className="flex flex-wrap gap-2">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-6 w-16 bg-violet-500/10 rounded-full" />
                ))}
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {topKeywords?.top_keywords?.slice(0, 8).map((kw: any, idx: number) => (
                  <Badge
                    key={kw.keyword}
                    variant="outline"
                    className={`
                      text-xs transition-all hover:scale-105 cursor-default
                      ${idx === 0 ? 'bg-violet-500/30 text-violet-200 border-violet-500/50' : ''}
                      ${idx === 1 ? 'bg-violet-500/20 text-violet-300 border-violet-500/40' : ''}
                      ${idx === 2 ? 'bg-violet-500/15 text-violet-300 border-violet-500/30' : ''}
                      ${idx > 2 ? 'text-violet-300/70 border-violet-500/20' : ''}
                    `}
                  >
                    {kw.keyword}
                    <span className="ml-1 opacity-60">({kw.total_articles})</span>
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
