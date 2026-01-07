'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { BarChart3, TrendingUp, Zap, Clock, Database, RefreshCw } from 'lucide-react';
import { fadeInFromBottom, staggerContainer } from '@/lib/animations-3d';
import { useAnalyticsSummary } from '@/hooks/use-analytics';

// Animated counter for smooth number transitions
function AnimatedValue({ value, suffix = '' }: { value: number; suffix?: string }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (value === 0) {
      setDisplayValue(0);
      return;
    }

    const duration = 1500;
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
  }, [value]);

  // Format large numbers
  const formatValue = (num: number) => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  return <>{formatValue(displayValue)}{suffix}</>;
}

export const StatsPreview3D = () => {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });
  const { data: summary, isLoading, dataUpdatedAt } = useAnalyticsSummary();
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    if (dataUpdatedAt) {
      const updateTime = new Date(dataUpdatedAt);
      setLastUpdate(updateTime.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }));
    }
  }, [dataUpdatedAt]);

  const stats = [
    {
      icon: BarChart3,
      label: 'Articles analyses',
      value: summary?.total_articles || 0,
      suffix: '+',
      color: 'violet'
    },
    {
      icon: TrendingUp,
      label: 'Score moyen (7j)',
      value: Math.round(summary?.avg_score_last_7_days || 0),
      suffix: '',
      color: 'magenta'
    },
    {
      icon: Zap,
      label: 'Tendances detectees',
      value: summary?.top_trends?.length || 0,
      suffix: '',
      color: 'violet'
    },
    {
      icon: Clock,
      label: "Scraped aujourd'hui",
      value: summary?.articles_scraped_today || 0,
      suffix: '',
      color: 'green'
    },
    {
      icon: Database,
      label: 'Sources actives',
      value: summary?.total_sources || 0,
      suffix: '',
      color: 'blue'
    },
  ];

  return (
    <motion.section
      ref={ref}
      className="relative z-10 w-full max-w-6xl mx-auto px-4 py-16"
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={staggerContainer}
    >
      {/* Header with live indicator */}
      <motion.div
        className="flex flex-col items-center mb-12"
        variants={fadeInFromBottom}
      >
        <h2 className="text-3xl font-bold text-center text-gradient-violet mb-3">
          Statistiques en temps reel
        </h2>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-500/20 border border-green-500/30">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-xs font-medium text-green-400">Live</span>
          </div>
          {lastUpdate && (
            <div className="flex items-center gap-1.5 text-xs text-violet-300/50">
              <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
              <span>MAJ: {lastUpdate}</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* Stats grid */}
      <motion.div
        className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-12"
        variants={staggerContainer}
      >
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          const colorClasses: Record<string, string> = {
            violet: 'text-violet-400 border-violet-500/30 from-violet-500/20',
            magenta: 'text-pink-400 border-pink-500/30 from-pink-500/20',
            green: 'text-green-400 border-green-500/30 from-green-500/20',
            blue: 'text-blue-400 border-blue-500/30 from-blue-500/20',
          };
          const colors = colorClasses[stat.color] || colorClasses.violet;

          return (
            <motion.div
              key={index}
              className={`p-5 rounded-xl bg-gradient-to-br ${colors.split(' ')[2]} to-transparent border ${colors.split(' ')[1]} backdrop-blur-sm transition-all hover:scale-[1.02]`}
              variants={fadeInFromBottom}
            >
              <Icon className={`w-7 h-7 ${colors.split(' ')[0]} mb-3`} />
              <div className="text-3xl font-bold text-violet-100 mb-1">
                {isLoading ? (
                  <span className="text-violet-300/50">--</span>
                ) : (
                  <AnimatedValue value={stat.value} suffix={stat.suffix} />
                )}
              </div>
              <div className="text-xs text-violet-300/70">{stat.label}</div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Power BI Placeholder */}
      <motion.div
        className="w-full h-96 rounded-2xl bg-gradient-to-br from-anthracite-800 to-anthracite-900 border border-violet/20 flex items-center justify-center relative overflow-hidden"
        variants={fadeInFromBottom}
      >
        <div className="absolute inset-0 bg-gradient-subtle" />
        <div className="relative z-10 text-center">
          <BarChart3 className="w-16 h-16 text-violet-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2 text-gradient-violet">Power BI Dashboard</h3>
          <p className="text-violet-300/60">
            Interactive visualizations coming soon
          </p>
        </div>
      </motion.div>
    </motion.section>
  );
};
