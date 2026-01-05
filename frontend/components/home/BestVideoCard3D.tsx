'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Play, ExternalLink } from 'lucide-react';
import { card3DLift, fadeInFromBottom } from '@/lib/animations-3d';
import { usePrefersReducedMotion } from '@/lib/scroll-parallax';
import type { Video } from '@/types';

interface BestVideoCard3DProps {
  video: Video | null;
}

export const BestVideoCard3D = ({ video }: BestVideoCard3DProps) => {
  const { ref, inView } = useInView({ threshold: 0.3, triggerOnce: true });
  const prefersReducedMotion = usePrefersReducedMotion();

  if (!video) {
    return (
      <div className="w-full h-96 rounded-2xl bg-anthracite-800/50 border border-magenta/20 flex items-center justify-center">
        <p className="text-violet-300/60">No video this week</p>
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
        className="relative h-full rounded-2xl bg-gradient-to-br from-anthracite-800 to-anthracite-900 border border-violet/30 overflow-hidden group"
        variants={prefersReducedMotion ? {} : card3DLift}
        initial="initial"
        whileHover="hover"
        style={{
          transformStyle: 'preserve-3d',
          willChange: 'transform',
        }}
      >
        {/* Thumbnail */}
        <div className="absolute inset-0">
          <img
            src={video.thumbnail_url || `https://img.youtube.com/vi/${video.video_id}/maxresdefault.jpg`}
            alt={video.title}
            className="w-full h-full object-cover opacity-60 group-hover:opacity-80 group-hover:scale-105 transition-all duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-anthracite-900 via-anthracite-900/60 to-transparent" />
        </div>

        {/* Play button overlay */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="w-16 h-16 rounded-full bg-violet/80 flex items-center justify-center">
            <Play className="w-8 h-8 text-white fill-white ml-1" />
          </div>
        </div>

        {/* Content */}
        <div className="relative z-10 h-full flex flex-col p-6">
          <div className="flex items-center gap-2 mb-auto">
            <span className="px-3 py-1 bg-violet/30 border border-violet/40 rounded-full text-xs font-semibold text-violet-200 backdrop-blur-sm">
              Video of the week
            </span>
          </div>

          <div className="mt-auto">
            <h3 className="text-xl font-bold mb-2 line-clamp-2 text-white drop-shadow-lg">
              {video.title}
            </h3>

            <div className="flex items-center justify-between">
              <div className="flex flex-col gap-1">
                <span className="text-xs text-violet-200/80 capitalize">
                  {video.source_type?.replace('_', ' ') || 'YouTube'}
                </span>
                {video.author && (
                  <span className="text-sm font-medium text-violet-100">{video.author}</span>
                )}
              </div>

              <a
                href={video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 rounded-full bg-violet/30 hover:bg-violet/50 backdrop-blur-sm transition-colors"
              >
                <ExternalLink className="w-5 h-5 text-violet-100" />
              </a>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
