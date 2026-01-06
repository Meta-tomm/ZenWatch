'use client';

import { CommentCard } from './CommentCard';
import type { Comment } from '@/types/auth';

interface CommentThreadProps {
  comments: Comment[];
  onEdit: (id: number, content: string) => void;
  onDelete: (id: number) => void;
  onReply: (parentId: number, content: string) => void;
  isEditing?: boolean;
  isDeleting?: boolean;
  depth?: number;
}

const MAX_DEPTH = 3;

export const CommentThread = ({
  comments,
  onEdit,
  onDelete,
  onReply,
  isEditing,
  isDeleting,
  depth = 0,
}: CommentThreadProps) => {
  if (!comments || comments.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {comments.map((comment) => (
        <div key={comment.id} className="space-y-3">
          <CommentCard
            comment={comment}
            onEdit={onEdit}
            onDelete={onDelete}
            onReply={onReply}
            isEditing={isEditing}
            isDeleting={isDeleting}
          />

          {comment.replies && comment.replies.length > 0 && depth < MAX_DEPTH && (
            <div className="ml-8 pl-4 border-l-2 border-muted">
              <CommentThread
                comments={comment.replies}
                onEdit={onEdit}
                onDelete={onDelete}
                onReply={onReply}
                isEditing={isEditing}
                isDeleting={isDeleting}
                depth={depth + 1}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
