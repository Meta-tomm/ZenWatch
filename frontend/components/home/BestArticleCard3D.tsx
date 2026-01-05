'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { ExternalLink, TrendingUp } from 'lucide-react';
import { card3DLift, fadeInFromBottom } from '@/lib/animations-3d';
import { usePrefersReducedMotion } from '@/lib/scroll-parallax';
import type { Article } from '@/types';

interface BestArticleCard3DProps {
  article: Article | null;
}

export const BestArticleCard3D = ({ article }: BestArticleCard3DProps) => {
  const { ref, inView } = useInView({ threshold: 0.3, triggerOnce: true });
  const prefersReducedMotion = usePrefersReducedMotion();

  if (!article) {
    return (
      <div className="w-full h-96 rounded-2xl bg-anthracite-800/50 border border-violet/20 flex items-center justify-center">
        <p className="text-violet-300/60">No article this week</p>
      </div>
    );
  }

  return (
    <motion.div
      ref={ref}
      className="w-full h-96 perspective-1000"
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={fadeInFromBottom}
    >
      <motion.div
        className="relative h-full rounded-2xl bg-gradient-to-br from-anthracite-800 to-anthracite-900 border border-violet/30 p-8 overflow-hidden group"
        variants={prefersReducedMotion ? {} : card3DLift}
        initial="initial"
        whileHover="hover"
        style={{
          transformStyle: 'preserve-3d',
          willChange: 'transform',
        }}
      >
        {/* Glow effect */}
        <div className="absolute inset-0 bg-gradient-glow opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        {/* Content */}
        <div className="relative z-10 h-full flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-3 py-1 bg-violet/20 border border-violet/30 rounded-full text-xs font-semibold text-violet-300">
              Article of the week
            </span>
            <div className="flex items-center gap-1 text-sm text-violet-300/70">
              <TrendingUp className="w-4 h-4" />
              <span>{article.score.toFixed(0)}</span>
            </div>
          </div>

          <h3 className="text-2xl font-bold mb-4 line-clamp-3 text-violet-100 group-hover:text-gradient-violet transition-all">
            {article.title}
          </h3>

          {article.summary && (
            <p className="text-violet-200/70 leading-relaxed line-clamp-4 mb-6">
              {article.summary}
            </p>
          )}

          <div className="mt-auto flex items-center justify-between">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-violet-300/60 capitalize">
                {article.source_type}
              </span>
              {article.author && (
                <span className="text-sm font-medium text-violet-200">{article.author}</span>
              )}
            </div>

            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-full bg-violet/20 hover:bg-violet/30 transition-colors"
            >
              <ExternalLink className="w-5 h-5 text-violet-light" />
            </a>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
