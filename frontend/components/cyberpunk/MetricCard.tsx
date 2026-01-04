'use client';

import { cn } from '@/lib/utils';
import { CornerBrackets } from './CornerBrackets';

interface MetricCardProps {
  value: string | number;
  label: string;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
  color?: 'gold' | 'gold-light' | 'gold-dark';
}

/**
 * Displays a metric/statistic with minimalist gold styling.
 * Includes corner brackets and optional trend indicator.
 *
 * @example
 * <MetricCard
 *   value={42}
 *   label="Total Articles"
 *   trend="up"
 *   color="gold"
 * />
 */
export const MetricCard = ({
  value,
  label,
  trend,
  className,
  color = 'gold',
}: MetricCardProps) => {
  const colorMap = {
    'gold': 'text-gold border-gold/30',
    'gold-light': 'text-gold-light border-gold-light/30',
    'gold-dark': 'text-gold-dark border-gold-dark/30',
  };

  const trendIcons = {
    up: '↗',
    down: '↘',
    neutral: '→',
  };

  return (
    <CornerBrackets color={color} className={className}>
      <div className={cn(
        'p-6 bg-black/50 border rounded-lg backdrop-blur-sm',
        'transition-all duration-300 hover:bg-black/70',
        colorMap[color]
      )}>
        <div className="flex items-baseline justify-between gap-2">
          <div className={cn(
            'text-4xl font-bold tabular-nums',
            'glow-text',
            colorMap[color].split(' ')[0]
          )}>
            {value}
          </div>
          {trend && (
            <span className="text-2xl opacity-70" aria-label={`Trend: ${trend}`}>
              {trendIcons[trend]}
            </span>
          )}
        </div>
        <div className="mt-2 text-sm uppercase tracking-wider opacity-70">
          {label}
        </div>
      </div>
    </CornerBrackets>
  );
};
