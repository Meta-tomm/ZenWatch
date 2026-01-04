'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LikeDislikeButtonsProps {
  initialLikes?: number;
  initialDislikes?: number;
  userReaction?: 'like' | 'dislike' | null;
  onLike?: () => void;
  onDislike?: () => void;
  size?: 'sm' | 'md' | 'lg';
  showCounts?: boolean;
}

export const LikeDislikeButtons = ({
  initialLikes = 0,
  initialDislikes = 0,
  userReaction,
  onLike,
  onDislike,
  size = 'md',
  showCounts = true,
}: LikeDislikeButtonsProps) => {
  const [localReaction, setLocalReaction] = useState(userReaction);
  const [likes, setLikes] = useState(initialLikes);
  const [dislikes, setDislikes] = useState(initialDislikes);

  const handleLike = () => {
    if (localReaction === 'like') {
      // Remove like
      setLocalReaction(null);
      setLikes(likes - 1);
    } else if (localReaction === 'dislike') {
      // Switch from dislike to like
      setLocalReaction('like');
      setLikes(likes + 1);
      setDislikes(dislikes - 1);
    } else {
      // Add like
      setLocalReaction('like');
      setLikes(likes + 1);
    }
    onLike?.();
  };

  const handleDislike = () => {
    if (localReaction === 'dislike') {
      // Remove dislike
      setLocalReaction(null);
      setDislikes(dislikes - 1);
    } else if (localReaction === 'like') {
      // Switch from like to dislike
      setLocalReaction('dislike');
      setDislikes(dislikes + 1);
      setLikes(likes - 1);
    } else {
      // Add dislike
      setLocalReaction('dislike');
      setDislikes(dislikes + 1);
    }
    onDislike?.();
  };

  const iconSize = size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4';
  const buttonSize = size === 'sm' ? 'sm' : size === 'lg' ? 'default' : 'sm';

  return (
    <div className="flex items-center gap-1">
      <Button
        variant="ghost"
        size={buttonSize}
        onClick={handleLike}
        className={cn(
          'gap-1.5',
          localReaction === 'like' && 'text-gold-dark hover:text-gold-dark'
        )}
      >
        <ThumbsUp
          className={cn(
            iconSize,
            localReaction === 'like' && 'fill-current'
          )}
        />
        {showCounts && <span className="text-xs">{likes}</span>}
      </Button>

      <Button
        variant="ghost"
        size={buttonSize}
        onClick={handleDislike}
        className={cn(
          'gap-1.5',
          localReaction === 'dislike' && 'text-red-500 hover:text-red-500'
        )}
      >
        <ThumbsDown
          className={cn(
            iconSize,
            localReaction === 'dislike' && 'fill-current'
          )}
        />
        {showCounts && <span className="text-xs">{dislikes}</span>}
      </Button>
    </div>
  );
};
