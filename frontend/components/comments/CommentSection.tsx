'use client';

import { MessageSquare, Loader2 } from 'lucide-react';
import { CommentForm } from './CommentForm';
import { CommentThread } from './CommentThread';
import { useComments } from '@/hooks/use-comments';
import { useCurrentUser } from '@/hooks/use-current-user';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface CommentSectionProps {
  articleId?: number;
  videoId?: number;
}

export const CommentSection = ({ articleId, videoId }: CommentSectionProps) => {
  const { user, isAuthenticated } = useCurrentUser();
  const {
    comments,
    isLoading,
    error,
    createComment,
    updateComment,
    deleteComment,
    isCreating,
    isUpdating,
    isDeleting,
  } = useComments({ articleId, videoId });

  const handleCreate = (content: string) => {
    createComment({
      content,
      article_id: articleId,
      video_id: videoId,
    });
  };

  const handleReply = (parentId: number, content: string) => {
    createComment({
      content,
      article_id: articleId,
      video_id: videoId,
      parent_id: parentId,
    });
  };

  const handleEdit = (id: number, content: string) => {
    updateComment({ id, content });
  };

  const handleDelete = (id: number) => {
    deleteComment(id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <MessageSquare className="h-5 w-5 text-violet-400" />
        <h3 className="text-lg font-semibold text-violet-200">
          Comments ({comments.length})
        </h3>
      </div>

      {/* Comment form or login prompt */}
      {isAuthenticated ? (
        <CommentForm
          onSubmit={handleCreate}
          isSubmitting={isCreating}
          placeholder="Share your thoughts..."
        />
      ) : (
        <div className="p-4 bg-anthracite-800/50 border border-violet-500/20 rounded-lg text-center">
          <p className="text-violet-300/70 mb-3">
            Sign in to join the discussion
          </p>
          <div className="flex items-center justify-center gap-3">
            <Button asChild variant="outline" size="sm">
              <Link href="/login">Sign In</Link>
            </Button>
            <Button asChild size="sm" className="bg-violet-600 hover:bg-violet-700">
              <Link href="/register">Create Account</Link>
            </Button>
          </div>
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-violet-500" />
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <p className="text-red-400 text-sm">
            Failed to load comments. Please try again.
          </p>
        </div>
      )}

      {/* Comments list */}
      {!isLoading && !error && (
        <CommentThread
          comments={comments}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onReply={handleReply}
          isUpdating={isUpdating}
          isDeleting={isDeleting}
        />
      )}
    </div>
  );
};
