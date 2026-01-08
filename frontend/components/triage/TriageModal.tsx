'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  X,
  Bookmark,
  ExternalLink,
  Video,
  TrendingUp,
  MessageSquare,
} from 'lucide-react';
import { formatRelativeDate } from '@/lib/date-utils';
import { cn } from '@/lib/utils';
import type { Article } from '@/types';

interface TriageModalProps {
  article: Article | null;
  isOpen: boolean;
  onClose: () => void;
  onDismiss: () => void;
  onBookmark: () => void;
}

export const TriageModal = ({
  article,
  isOpen,
  onClose,
  onDismiss,
  onBookmark,
}: TriageModalProps) => {
  if (!article) return null;

  const isVideo = article.source_type === 'youtube' || article.source_type === 'video';

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal Container - centered */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="w-full max-w-2xl max-h-[85vh] flex flex-col bg-anthracite-950 border border-violet-500/30 rounded-2xl shadow-xl shadow-violet-500/10 overflow-hidden"
            >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-violet-500/20">
              <div className="flex items-center gap-2">
                {isVideo && (
                  <Badge className="bg-violet-600/80 text-white">
                    <Video className="w-3 h-3 mr-1" />
                    Video
                  </Badge>
                )}
                <span className="text-sm text-violet-300/60 capitalize">
                  {article.source_type}
                </span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="text-violet-300/70 hover:text-violet-200"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Title */}
              <h2 className="text-2xl font-bold text-violet-100 leading-tight">
                {article.title}
              </h2>

              {/* Meta */}
              <div className="flex flex-wrap items-center gap-4 text-sm text-violet-300/60">
                <span>{formatRelativeDate(article.published_at)}</span>
                {article.read_time_minutes && (
                  <span>{article.read_time_minutes} min read</span>
                )}
                {article.author && <span>by {article.author}</span>}
              </div>

              {/* Score & Stats */}
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <span className={cn(
                    'text-4xl font-bold',
                    article.score >= 70 ? 'text-violet-400' : article.score >= 50 ? 'text-violet-300' : 'text-violet-300/70'
                  )}>
                    {article.score?.toFixed(0) || 'N/A'}
                  </span>
                  <span className="text-sm text-violet-300/50">score</span>
                </div>

                <div className="flex items-center gap-4 text-violet-300/50">
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    <span>{article.upvotes || 0}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <MessageSquare className="w-4 h-4" />
                    <span>{article.comments_count || 0}</span>
                  </div>
                </div>
              </div>

              {/* Category & Tags */}
              <div className="flex flex-wrap gap-2">
                <Badge
                  variant="secondary"
                  className="bg-violet-500/20 text-violet-200 border-violet-400/30"
                >
                  {article.category}
                </Badge>
                {(article.tags || [])
                  .filter((tag) => tag && tag.trim())
                  .map((tag) => (
                    <Badge
                      key={tag}
                      variant="outline"
                      className="border-violet-500/30 text-violet-300/70"
                    >
                      {tag}
                    </Badge>
                  ))}
              </div>

              {/* Summary */}
              {article.summary && (
                <div>
                  <h3 className="text-sm font-semibold text-violet-200 mb-2">Summary</h3>
                  <p className="text-violet-200/70 leading-relaxed">
                    {article.summary}
                  </p>
                </div>
              )}

              {/* Content preview */}
              {article.content && (
                <div>
                  <h3 className="text-sm font-semibold text-violet-200 mb-2">Preview</h3>
                  <p className="text-violet-200/60 leading-relaxed line-clamp-6">
                    {article.content}
                  </p>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between p-4 border-t border-violet-500/20 bg-anthracite-900/50">
              <Button
                variant="ghost"
                onClick={() => {
                  onDismiss();
                  onClose();
                }}
                className="text-red-400 hover:text-red-300 hover:bg-red-500/20"
              >
                <X className="w-5 h-5 mr-2" />
                Skip
              </Button>

              <Button
                variant="ghost"
                asChild
                className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
              >
                <a href={article.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Open Article
                </a>
              </Button>

              <Button
                onClick={() => {
                  onBookmark();
                  onClose();
                }}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                <Bookmark className="w-5 h-5 mr-2" />
                Save
              </Button>
            </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
