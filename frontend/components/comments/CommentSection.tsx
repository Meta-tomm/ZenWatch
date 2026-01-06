'use client';

import { MessageCircle } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { useComments } from '@/hooks/use-comments';
import { CommentForm } from './CommentForm';
import { CommentThread } from './CommentThread';

interface CommentSectionProps {
  contentType: 'article' | 'video';
  contentId: number;
}

export const CommentSection = ({ contentType, contentId }: CommentSectionProps) => {
  const {
    comments,
    isLoading,
    addComment,
    editComment,
    removeComment,
    isAdding,
    isEditing,
    isDeleting,
  } = useComments(contentType, contentId);

  const handleReply = (parentId: number, content: string) => {
    addComment(content, parentId);
  };

  const rootComments = comments.filter((c) => !c.parent_id);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5" />
          <Skeleton className="h-6 w-32" />
        </div>
        <Skeleton className="h-24 w-full" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-3">
              <Skeleton className="h-8 w-8 rounded-full" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-16 w-full" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <MessageCircle className="h-5 w-5" />
        <h3 className="font-semibold">
          {comments.length} commentaire{comments.length !== 1 ? 's' : ''}
        </h3>
      </div>

      <CommentForm onSubmit={addComment} isSubmitting={isAdding} />

      {rootComments.length > 0 ? (
        <CommentThread
          comments={rootComments}
          onEdit={editComment}
          onDelete={removeComment}
          onReply={handleReply}
          isEditing={isEditing}
          isDeleting={isDeleting}
        />
      ) : (
        <p className="text-center text-muted-foreground py-8">
          Aucun commentaire pour le moment. Soyez le premier a commenter !
        </p>
      )}
    </div>
  );
};
