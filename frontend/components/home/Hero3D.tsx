'use client';

import { motion } from 'framer-motion';
import { fadeInFromBottom } from '@/lib/animations-3d';

export const Hero3D = () => {
  return (
    <motion.section
      className="relative z-10 min-h-[40vh] flex flex-col items-center justify-center px-4 py-16"
      initial="hidden"
      animate="visible"
      variants={fadeInFromBottom}
    >
      <motion.h1
        className="text-6xl md:text-8xl font-bold text-center mb-4 text-gradient-violet"
        style={{
          textShadow: '0 0 40px rgba(139, 92, 246, 0.5), 0 0 80px rgba(217, 70, 239, 0.3)',
        }}
      >
        ZENWATCH
      </motion.h1>

      <motion.p
        className="text-xl md:text-2xl text-muted-foreground text-center max-w-2xl"
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
          className="px-6 py-3 bg-gradient-violet-magenta rounded-lg font-semibold hover:opacity-90 transition-opacity"
        >
          Explore articles
        </a>
        <a
          href="/config"
          className="px-6 py-3 border border-violet/30 rounded-lg font-semibold hover:bg-violet/10 transition-colors"
        >
          Configure
        </a>
      </motion.div>
    </motion.section>
  );
};
