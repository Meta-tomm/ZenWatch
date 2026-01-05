'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { BarChart3, TrendingUp, Zap } from 'lucide-react';
import { fadeInFromBottom, staggerContainer } from '@/lib/animations-3d';

export const StatsPreview3D = () => {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });

  const stats = [
    { icon: BarChart3, label: 'Articles analyzed', value: '2.5K+', color: 'violet' },
    { icon: TrendingUp, label: 'Average score', value: '87', color: 'magenta' },
    { icon: Zap, label: 'Trends detected', value: '24', color: 'violet' },
  ];

  return (
    <motion.section
      ref={ref}
      className="relative z-10 w-full max-w-6xl mx-auto px-4 py-16"
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={staggerContainer}
    >
      <motion.h2
        className="text-3xl font-bold text-center mb-12 text-gradient-violet"
        variants={fadeInFromBottom}
      >
        Real-time statistics
      </motion.h2>

      {/* Stats grid */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
        variants={staggerContainer}
      >
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={index}
              className="p-6 rounded-xl bg-anthracite-800/50 border border-violet/20 backdrop-blur-sm"
              variants={fadeInFromBottom}
            >
              <Icon className={`w-8 h-8 text-${stat.color} mb-4`} />
              <div className="text-4xl font-bold text-gradient-violet mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-violet-300/70">{stat.label}</div>
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
