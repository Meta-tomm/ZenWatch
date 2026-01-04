'use client';

import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animations';

interface AnimatedTitleProps {
  title: string;
  subtitle?: string;
  className?: string;
}

/**
 * Minimalist animated hero title with subtle fade-in animation.
 * Uses Framer Motion for smooth entrance animation with gold accent.
 *
 * @example
 * <AnimatedTitle
 *   title="ZENWATCH"
 *   subtitle="Your AI-Powered Tech Intelligence Platform"
 * />
 */
export const AnimatedTitle = ({
  title,
  subtitle,
  className = '',
}: AnimatedTitleProps) => {
  return (
    <motion.div
      className={className}
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
    >
      <h1 className="text-6xl md:text-8xl font-bold text-gold glow-text tracking-tight">
        {title}
      </h1>
      {subtitle && (
        <motion.p
          className="mt-4 text-xl md:text-2xl text-gray-400"
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.2 }}
        >
          {subtitle}
        </motion.p>
      )}
    </motion.div>
  );
};
