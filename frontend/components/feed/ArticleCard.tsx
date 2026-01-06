"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Star,
  ExternalLink,
  MessageSquare,
  TrendingUp,
  BookmarkPlus,
} from "lucide-react";
import { LikeDislikeButtons } from "./LikeDislikeButtons";
import { useToggleFavorite } from "@/hooks/use-toggle-favorite";
import { useToggleBookmark } from "@/hooks/use-library";
import { formatRelativeDate } from "@/lib/date-utils";
import { minimalFadeIn } from "@/lib/animations-3d";
import { cn } from "@/lib/utils";
import { articlesApi } from "@/lib/api-client";
import type { Article } from "@/types";

interface ArticleCardProps {
  article: Article;
  onOpenModal?: (id: string) => void;
}

export const ArticleCard = ({ article, onOpenModal }: ArticleCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [localArticle, setLocalArticle] = useState(article);
  const toggleFavorite = useToggleFavorite();
  const toggleBookmark = useToggleBookmark();

  const handleLike = async () => {
    try {
      const updated = await articlesApi.toggleLike(localArticle.id);
      setLocalArticle(updated);
    } catch (err) {
      console.error("Failed to like article:", err);
    }
  };

  const handleDislike = async () => {
    try {
      const updated = await articlesApi.toggleDislike(localArticle.id);
      setLocalArticle(updated);
    } catch (err) {
      console.error("Failed to dislike article:", err);
    }
  };

  const scoreColor =
    localArticle.score >= 70
      ? "text-violet-400"
      : localArticle.score >= 50
        ? "text-violet-300"
        : "text-muted-foreground";

  return (
    <motion.div variants={minimalFadeIn} initial="hidden" animate="visible">
      <div
        className={cn(
          "p-4 bg-anthracite-800/80 border border-violet-500/30 rounded-lg",
          "hover:bg-anthracite-700/80 hover:border-violet-400/50 transition-all duration-300",
          localArticle.is_read && "opacity-60",
        )}
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex-1 min-w-0">
            <h3
              className={cn(
                "font-semibold leading-tight mb-1 cursor-pointer hover:text-violet-300 line-clamp-2 transition-colors text-violet-100",
                localArticle.score >= 70 && "text-violet-200",
              )}
              onClick={() => onOpenModal?.(localArticle.id)}
            >
              {localArticle.title}
            </h3>
            <div className="flex items-center gap-2 text-xs text-violet-300/60">
              <span className="capitalize">{localArticle.source_type}</span>
              <span>•</span>
              <span>{formatRelativeDate(localArticle.published_at)}</span>
              {localArticle.read_time_minutes && (
                <>
                  <span>•</span>
                  <span>{localArticle.read_time_minutes} min</span>
                </>
              )}
            </div>
          </div>

          {/* Score */}
          <div className="flex flex-col items-center shrink-0">
            <div className={cn("text-2xl font-bold", scoreColor)}>
              {localArticle.score != null
                ? localArticle.score.toFixed(0)
                : "N/A"}
            </div>
            <div className="text-xs text-muted-foreground">score</div>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          <Badge
            variant="secondary"
            className="text-xs bg-violet-500/20 text-violet-200 border-violet-400/30"
          >
            {localArticle.category}
          </Badge>
          {(localArticle.tags || [])
            .filter((tag) => tag && tag.trim())
            .slice(0, 3)
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

        {/* Summary */}
        {localArticle.summary && (
          <p
            className={cn(
              "text-sm text-violet-200/70 leading-relaxed mb-3",
              !isExpanded && "line-clamp-2",
            )}
          >
            {localArticle.summary}
          </p>
        )}

        {/* Stats */}
        <div className="flex items-center gap-4 mb-3 text-xs text-violet-300/50">
          <div className="flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            {localArticle.upvotes || 0}
          </div>
          <div className="flex items-center gap-1">
            <MessageSquare className="w-3 h-3" />
            {localArticle.comments_count || 0}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between border-t border-violet-500/20 pt-3">
          <div className="flex items-center gap-2">
            <LikeDislikeButtons
              initialLikes={localArticle.likes}
              initialDislikes={localArticle.dislikes}
              userReaction={localArticle.user_reaction}
              onLike={handleLike}
              onDislike={handleDislike}
              size="sm"
            />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleFavorite.mutate(localArticle.id)}
              className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
            >
              <Star
                className={cn(
                  "w-4 h-4",
                  localArticle.is_favorite && "fill-violet-400 text-violet-400",
                )}
              />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleBookmark.mutate(localArticle.id)}
              className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
            >
              <BookmarkPlus
                className={cn(
                  "w-4 h-4",
                  localArticle.is_bookmarked && "fill-violet-400 text-violet-400"
                )}
              />
            </Button>
          </div>

          <div className="flex items-center gap-1">
            {localArticle.summary && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
              >
                {isExpanded ? "Less" : "More"}
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              asChild
              className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
            >
              <a
                href={localArticle.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
