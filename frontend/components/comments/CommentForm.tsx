'use client';

import { useState } from 'react';
import { Loader2, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

interface CommentFormProps {
  onSubmit: (content: string) => void;
  isSubmitting?: boolean;
  placeholder?: string;
  autoFocus?: boolean;
  onCancel?: () => void;
  initialValue?: string;
}

export const CommentForm = ({
  onSubmit,
  isSubmitting = false,
  placeholder = 'Write a comment...',
  autoFocus = false,
  onCancel,
  initialValue = '',
}: CommentFormProps) => {
  const [content, setContent] = useState(initialValue);
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (content.trim() && !isSubmitting) {
      onSubmit(content.trim());
      setContent('');
    }
  };

  const showActions = isFocused || content.trim().length > 0;

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <Textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        disabled={isSubmitting}
        className={cn(
          'min-h-[80px] resize-none transition-all duration-200',
          'bg-anthracite-800 border-violet-500/30 text-violet-100',
          'placeholder:text-violet-300/50',
          'focus:border-violet-500 focus:ring-violet-500/20',
          showActions && 'min-h-[100px]'
        )}
      />

      {showActions && (
        <div className="flex items-center justify-end gap-2">
          {onCancel && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={onCancel}
              disabled={isSubmitting}
              className="text-violet-300/70 hover:text-violet-200"
            >
              Cancel
            </Button>
          )}
          <Button
            type="submit"
            size="sm"
            disabled={!content.trim() || isSubmitting}
            className="bg-violet-600 hover:bg-violet-700 text-white"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Posting...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Post
              </>
            )}
          </Button>
        </div>
      )}
    </form>
  );
};
