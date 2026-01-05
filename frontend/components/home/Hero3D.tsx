'use client';

import { motion } from 'framer-motion';
import { fadeInFromBottom } from '@/lib/animations-3d';
import { usePrefersReducedMotion } from '@/lib/scroll-parallax';

export const Hero3D = () => {
  const prefersReducedMotion = usePrefersReducedMotion();

  return (
    <motion.section
      className="relative z-10 min-h-[40vh] flex flex-col items-center justify-center px-4 py-16"
      initial="hidden"
      animate="visible"
      variants={fadeInFromBottom}
    >
      <motion.h1
        className="text-6xl md:text-8xl font-bold text-center mb-4 relative"
        style={{
          perspective: '1000px',
          transformStyle: 'preserve-3d',
        }}
        animate={prefersReducedMotion ? {} : {
          rotateX: [0, 2, 0, -2, 0],
          rotateY: [0, -3, 0, 3, 0],
          scale: [1, 1.02, 1, 1.02, 1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        {/* Glow layer */}
        <span
          className="absolute inset-0 blur-2xl opacity-50 text-gradient-violet"
          aria-hidden="true"
          style={{
            animation: prefersReducedMotion ? 'none' : 'pulseGlow 4s ease-in-out infinite',
          }}
        >
          ZENWATCH
        </span>

        {/* Main text with shimmer */}
        <span
          className="relative inline-block"
          style={{
            background: 'linear-gradient(90deg, #8b5cf6 0%, #d946ef 25%, #f0abfc 50%, #d946ef 75%, #8b5cf6 100%)',
            backgroundSize: '200% 100%',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            animation: prefersReducedMotion ? 'none' : 'shimmer 6s linear infinite',
            textShadow: '0 0 40px rgba(139, 92, 246, 0.5), 0 0 80px rgba(217, 70, 239, 0.3)',
          }}
        >
          ZENWATCH
        </span>
      </motion.h1>

      <motion.p
        className="text-xl md:text-2xl text-violet-300/80 text-center max-w-2xl"
        variants={fadeInFromBottom}
      >
        Your smart tech intelligence
      </motion.p>

      <motion.div
        className="mt-8 flex gap-4"
        variants={fadeInFromBottom}
      >
        <a
          href="/articles"
          className="px-6 py-3 bg-gradient-violet-magenta rounded-lg font-semibold text-white hover:opacity-90 transition-opacity"
        >
          Explore articles
        </a>
        <a
          href="/config"
          className="px-6 py-3 border border-violet/30 rounded-lg font-semibold text-violet-200 hover:bg-violet/10 transition-colors"
        >
          Configure
        </a>
      </motion.div>
    </motion.section>
  );
};
