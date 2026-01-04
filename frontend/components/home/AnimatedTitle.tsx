'use client';

import { motion } from 'framer-motion';
import { GlitchText } from '@/components/cyberpunk';
import { fadeInUp } from '@/lib/animations';

interface AnimatedTitleProps {
  title: string;
  subtitle?: string;
  className?: string;
}

/**
 * Animated hero title with glitch effect and fade-in animation.
 * Uses Framer Motion for entrance animation and GlitchText for cyberpunk effect.
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
      <GlitchText
        as="h1"
        className="text-6xl md:text-8xl font-bold text-cyber-blue glow-text tracking-tight"
      >
        {title}
      </GlitchText>
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
