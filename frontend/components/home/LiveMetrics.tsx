'use client';

import { motion } from 'framer-motion';
import { MetricCard } from '@/components/cyberpunk';
import { staggerContainer, staggerItem } from '@/lib/animations';

interface Metric {
  value: string | number;
  label: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'blue' | 'yellow' | 'green';
}

interface LiveMetricsProps {
  metrics: Metric[];
  className?: string;
}

/**
 * Displays a grid of live metrics with staggered entrance animations.
 * Uses MetricCard components with Framer Motion stagger effects.
 *
 * @example
 * <LiveMetrics metrics={[
 *   { value: 127, label: 'Articles Today', trend: 'up', color: 'blue' },
 *   { value: '99%', label: 'Relevance Score', color: 'green' }
 * ]} />
 */
export const LiveMetrics = ({ metrics, className = '' }: LiveMetricsProps) => {
  return (
    <motion.div
      className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
    >
      {metrics.map((metric, index) => (
        <motion.div key={index} variants={staggerItem}>
          <MetricCard
            value={metric.value}
            label={metric.label}
            trend={metric.trend}
            color={metric.color}
          />
        </motion.div>
      ))}
    </motion.div>
  );
};
