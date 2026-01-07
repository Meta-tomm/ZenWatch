'use client';

import { useEffect, useState } from 'react';
import { useAnalyticsSummary, useTopKeywords } from '@/hooks/use-analytics';
import {
  FileText,
  Activity,
  TrendingUp,
  Clock,
  Database,
  Tag,
  RefreshCw,
  Zap,
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

      // Easing function for smooth animation
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

// Stat card component
function StatCard({
  icon: Icon,
  label,
  value,
  trend,
  color = 'violet',
  isLoading = false,
}: {
  icon: React.ElementType;
  label: string;
  value: number;
  trend?: string;
  color?: 'violet' | 'green' | 'blue' | 'orange';
  isLoading?: boolean;
}) {
  const colors = {
    violet: 'from-violet-500/20 to-violet-600/5 border-violet-500/30 text-violet-400',
    green: 'from-green-500/20 to-green-600/5 border-green-500/30 text-green-400',
    blue: 'from-blue-500/20 to-blue-600/5 border-blue-500/30 text-blue-400',
    orange: 'from-orange-500/20 to-orange-600/5 border-orange-500/30 text-orange-400',
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-3 p-3 rounded-lg bg-gradient-to-r from-violet-500/10 to-transparent border border-violet-500/20">
        <Skeleton className="h-8 w-8 rounded-lg bg-violet-500/20" />
        <div className="space-y-1">
          <Skeleton className="h-3 w-16 bg-violet-500/10" />
          <Skeleton className="h-5 w-12 bg-violet-500/20" />
        </div>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg bg-gradient-to-r ${colors[color]} border`}>
      <div className={`p-2 rounded-lg bg-gradient-to-br ${colors[color]}`}>
        <Icon className="w-4 h-4" />
      </div>
      <div>
        <p className="text-xs text-violet-300/60">{label}</p>
        <p className="text-lg font-bold text-violet-100">
          <AnimatedCounter value={value} />
        </p>
        {trend && <p className="text-xs text-violet-300/50">{trend}</p>}
      </div>
    </div>
  );
}

export function RealTimeStats() {
  const { data: summary, isLoading: summaryLoading, dataUpdatedAt } = useAnalyticsSummary();
  const { data: topKeywords, isLoading: keywordsLoading } = useTopKeywords(7, 5);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  // Update last refresh time
  useEffect(() => {
    if (dataUpdatedAt) {
      const updateTime = new Date(dataUpdatedAt);
      setLastUpdate(updateTime.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }));
    }
  }, [dataUpdatedAt]);

  const isLoading = summaryLoading;

  return (
    <div className="border-b border-violet-500/20 bg-anthracite-900/80 backdrop-blur">
      <div className="container mx-auto px-4 py-4">
        {/* Header with refresh indicator */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-violet-400" />
            <h2 className="text-sm font-semibold text-violet-200">Statistiques en temps reel</h2>
            <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-500/20 border border-green-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs text-green-400">Live</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-violet-300/50">
            <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
            <span>MAJ: {lastUpdate || '--:--'}</span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <StatCard
            icon={FileText}
            label="Articles totaux"
            value={summary?.total_articles || 0}
            color="violet"
            isLoading={isLoading}
          />
          <StatCard
            icon={Clock}
            label="Aujourd'hui"
            value={summary?.articles_scraped_today || 0}
            color="green"
            isLoading={isLoading}
          />
          <StatCard
            icon={TrendingUp}
            label="Score moyen"
            value={Math.round(summary?.avg_score_last_7_days || 0)}
            trend="7 derniers jours"
            color="blue"
            isLoading={isLoading}
          />
          <StatCard
            icon={Database}
            label="Sources actives"
            value={summary?.total_sources || 0}
            color="orange"
            isLoading={isLoading}
          />
          <StatCard
            icon={Tag}
            label="Keywords"
            value={summary?.total_keywords || 0}
            color="violet"
            isLoading={isLoading}
          />
          <StatCard
            icon={Zap}
            label="Tendances"
            value={summary?.top_trends?.length || 0}
            color="green"
            isLoading={isLoading}
          />
        </div>

        {/* Trending Keywords */}
        {!keywordsLoading && topKeywords?.top_keywords && topKeywords.top_keywords.length > 0 && (
          <div className="mt-4 pt-4 border-t border-violet-500/10">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-violet-400" />
              <span className="text-xs font-medium text-violet-300">Top Keywords</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {topKeywords.top_keywords.map((kw: any, idx: number) => (
                <Badge
                  key={kw.keyword}
                  variant="outline"
                  className={`
                    text-xs transition-all hover:scale-105 cursor-default
                    ${idx === 0 ? 'bg-violet-500/20 text-violet-200 border-violet-500/40' : ''}
                    ${idx === 1 ? 'bg-violet-500/15 text-violet-300 border-violet-500/30' : ''}
                    ${idx === 2 ? 'bg-violet-500/10 text-violet-300 border-violet-500/20' : ''}
                    ${idx > 2 ? 'text-violet-300/70 border-violet-500/20' : ''}
                  `}
                >
                  {kw.keyword}
                  <span className="ml-1 text-violet-400/60">({kw.total_articles})</span>
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Categories breakdown (compact) */}
        {!isLoading && summary?.articles_by_category && Object.keys(summary.articles_by_category).length > 0 && (
          <div className="mt-3 pt-3 border-t border-violet-500/10">
            <div className="flex items-center gap-4 overflow-x-auto pb-1">
              <span className="text-xs text-violet-300/50 shrink-0">Par categorie:</span>
              {Object.entries(summary.articles_by_category)
                .sort(([, a], [, b]) => (b as number) - (a as number))
                .slice(0, 6)
                .map(([category, count]) => (
                  <div
                    key={category}
                    className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-anthracite-800/50 border border-violet-500/10 shrink-0"
                  >
                    <span className="text-xs text-violet-300 capitalize">{category}</span>
                    <span className="text-xs font-medium text-violet-100">{count as number}</span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
