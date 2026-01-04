'use client';

import { cn } from '@/lib/utils';
import { CornerBrackets } from './CornerBrackets';

interface MetricCardProps {
  value: string | number;
  label: string;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
  color?: 'blue' | 'yellow' | 'green';
}

/**
 * Displays a metric/statistic with cyberpunk styling.
 * Includes corner brackets, glow effects, and optional trend indicator.
 *
 * @example
 * <MetricCard
 *   value={42}
 *   label="Total Articles"
 *   trend="up"
 *   color="blue"
 * />
 */
export const MetricCard = ({
  value,
  label,
  trend,
  className,
  color = 'blue',
}: MetricCardProps) => {
  const colorMap = {
    blue: 'text-cyber-blue border-cyber-blue/30',
    yellow: 'text-cyber-yellow border-cyber-yellow/30',
    green: 'text-cyber-green border-cyber-green/30',
  };

  const trendIcons = {
    up: '↗',
    down: '↘',
    neutral: '→',
  };

  return (
    <CornerBrackets color={color} className={className}>
      <div className={cn(
        'p-6 bg-cyber-black/50 border rounded-lg backdrop-blur-sm',
        'transition-all duration-300 hover:bg-cyber-black/70',
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
