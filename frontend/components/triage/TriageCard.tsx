'use client';

import { useState } from 'react';
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Bookmark, X, Video, ExternalLink, ChevronDown } from 'lucide-react';
import { formatRelativeDate } from '@/lib/date-utils';
import { cn } from '@/lib/utils';
import type { Article } from '@/types';

interface TriageCardProps {
  article: Article;
  onSwipeLeft: () => void;
  onSwipeRight: () => void;
  onTap: () => void;
}

export const TriageCard = ({
  article,
  onSwipeLeft,
  onSwipeRight,
  onTap,
}: TriageCardProps) => {
  const [exitX, setExitX] = useState(0);
  const x = useMotionValue(0);

  // Transform x position to rotation and opacity
  const rotate = useTransform(x, [-200, 0, 200], [-15, 0, 15]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0.5, 1, 1, 1, 0.5]);

  // Indicator opacity based on drag direction
  const leftIndicatorOpacity = useTransform(x, [-100, 0], [1, 0]);
  const rightIndicatorOpacity = useTransform(x, [0, 100], [0, 1]);

  const isVideo = article.source_type === 'youtube' || article.source_type === 'video';

  const handleDragEnd = (_: any, info: PanInfo) => {
    const threshold = 100;
    if (info.offset.x > threshold) {
      setExitX(300);
      onSwipeRight();
    } else if (info.offset.x < -threshold) {
      setExitX(-300);
      onSwipeLeft();
    }
  };

  return (
    <div className="relative w-full max-w-md mx-auto">
      {/* Swipe indicators */}
      <motion.div
        style={{ opacity: leftIndicatorOpacity }}
        className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-16 z-10"
      >
        <div className="w-12 h-12 rounded-full bg-red-500/20 border-2 border-red-500 flex items-center justify-center">
          <X className="w-6 h-6 text-red-500" />
        </div>
        <span className="text-red-500 text-sm mt-1 block text-center">Skip</span>
      </motion.div>

      <motion.div
        style={{ opacity: rightIndicatorOpacity }}
        className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-16 z-10"
      >
        <div className="w-12 h-12 rounded-full bg-green-500/20 border-2 border-green-500 flex items-center justify-center">
          <Bookmark className="w-6 h-6 text-green-500" />
        </div>
        <span className="text-green-500 text-sm mt-1 block text-center">Save</span>
      </motion.div>

      {/* Card */}
      <motion.div
        style={{ x, rotate, opacity }}
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        onDragEnd={handleDragEnd}
        animate={{ x: exitX }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className={cn(
          'relative bg-anthracite-800 border border-violet-500/30 rounded-xl overflow-hidden cursor-grab active:cursor-grabbing',
          'shadow-lg shadow-violet-500/10'
        )}
      >
        {/* Video badge */}
        {isVideo && (
          <div className="absolute top-4 right-4 z-10">
            <Badge className="bg-violet-600/80 text-white">
              <Video className="w-3 h-3 mr-1" />
              Video
            </Badge>
          </div>
        )}

        <div className="p-6">
          {/* Title */}
          <h2 className="text-xl font-bold text-violet-100 mb-3 line-clamp-3">
            {article.title}
          </h2>

          {/* Meta */}
          <div className="flex items-center gap-3 text-sm text-violet-300/60 mb-4">
            <span className="capitalize">{article.source_type}</span>
            <span>-</span>
            <span>{formatRelativeDate(article.published_at)}</span>
            {article.read_time_minutes && (
              <>
                <span>-</span>
                <span>{article.read_time_minutes} min read</span>
              </>
            )}
          </div>

          {/* Score */}
          <div className="flex items-center gap-4 mb-4">
            <div className="flex items-center gap-2">
              <span className={cn(
                'text-3xl font-bold',
                article.score >= 70 ? 'text-violet-400' : article.score >= 50 ? 'text-violet-300' : 'text-violet-300/70'
              )}>
                {article.score?.toFixed(0) || 'N/A'}
              </span>
              <span className="text-sm text-violet-300/50">score</span>
            </div>

            <Badge
              variant="secondary"
              className="bg-violet-500/20 text-violet-200 border-violet-400/30"
            >
              {article.category}
            </Badge>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mb-4">
            {(article.tags || [])
              .filter((tag) => tag && tag.trim())
              .slice(0, 4)
              .map((tag) => (
                <Badge
                  key={tag}
                  variant="outline"
                  className="text-xs border-violet-500/30 text-violet-300/70"
                >
                  {tag}
                </Badge>
              ))}
          </div>

          {/* Summary preview */}
          {article.summary && (
            <p className="text-sm text-violet-200/70 leading-relaxed line-clamp-4 mb-4">
              {article.summary}
            </p>
          )}

          {/* Tap for more */}
          <Button
            variant="ghost"
            className="w-full text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
            onClick={(e) => {
              e.stopPropagation();
              onTap();
            }}
          >
            <ChevronDown className="w-4 h-4 mr-2" />
            Tap for more details
          </Button>
        </div>

        {/* Quick actions */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-violet-500/20 bg-anthracite-900/50">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              setExitX(-300);
              onSwipeLeft();
            }}
            className="text-red-400 hover:text-red-300 hover:bg-red-500/20"
          >
            <X className="w-5 h-5 mr-1" />
            Skip
          </Button>

          <Button
            variant="ghost"
            size="sm"
            asChild
            className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
          >
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
            >
              <ExternalLink className="w-4 h-4 mr-1" />
              Open
            </a>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              setExitX(300);
              onSwipeRight();
            }}
            className="text-green-400 hover:text-green-300 hover:bg-green-500/20"
          >
            <Bookmark className="w-5 h-5 mr-1" />
            Save
          </Button>
        </div>
      </motion.div>

      {/* Swipe hint */}
      <p className="text-center text-xs text-violet-300/50 mt-4">
        Swipe left to skip, right to save to library
      </p>
    </div>
  );
};
