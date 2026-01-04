'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Play, ExternalLink } from 'lucide-react';
import { card3DLift, fadeInFromBottom } from '@/lib/animations-3d';
import { usePrefersReducedMotion } from '@/lib/scroll-parallax';
import type { Article } from '@/types';

interface BestVideoCard3DProps {
  video: Article | null;
}

export const BestVideoCard3D = ({ video }: BestVideoCard3DProps) => {
  const { ref, inView } = useInView({ threshold: 0.3, triggerOnce: true });
  const prefersReducedMotion = usePrefersReducedMotion();

  if (!video) {
    return (
      <div className="w-full h-96 rounded-2xl bg-anthracite-800/50 border border-magenta/20 flex items-center justify-center">
        <p className="text-muted-foreground">Aucune vidéo cette semaine</p>
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
        className="relative h-full rounded-2xl bg-gradient-to-br from-anthracite-800 to-anthracite-900 border border-magenta/30 p-8 overflow-hidden group"
        variants={prefersReducedMotion ? {} : card3DLift}
        initial="initial"
        whileHover="hover"
        style={{
          transformStyle: 'preserve-3d',
          willChange: 'transform',
        }}
      >
        {/* Glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-magenta/20 to-violet/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        {/* Content */}
        <div className="relative z-10 h-full flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-3 py-1 bg-magenta/20 border border-magenta/30 rounded-full text-xs font-semibold text-magenta-light">
              Vidéo de la semaine
            </span>
            <Play className="w-4 h-4 text-magenta-light" />
          </div>

          <h3 className="text-2xl font-bold mb-4 line-clamp-3 group-hover:text-gradient-violet transition-all">
            {video.title}
          </h3>

          {video.summary && (
            <p className="text-muted-foreground leading-relaxed line-clamp-4 mb-6">
              {video.summary}
            </p>
          )}

          <div className="mt-auto flex items-center justify-between">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted-foreground capitalize">
                {video.source_type || 'YouTube'}
              </span>
              {video.author && (
                <span className="text-sm font-medium">{video.author}</span>
              )}
            </div>

            <a
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-full bg-magenta/20 hover:bg-magenta/30 transition-colors"
            >
              <ExternalLink className="w-5 h-5 text-magenta-light" />
            </a>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
