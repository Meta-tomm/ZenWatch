'use client';

import { CommentCard } from './CommentCard';
import type { Comment } from '@/types/auth';

interface CommentThreadProps {
  comments: Comment[];
  onEdit: (id: number, content: string) => void;
  onDelete: (id: number) => void;
  onReply: (parentId: number, content: string) => void;
  isUpdating?: boolean;
  isDeleting?: boolean;
}

export const CommentThread = ({
  comments,
  onEdit,
  onDelete,
  onReply,
  isUpdating,
  isDeleting,
}: CommentThreadProps) => {
  // Build tree structure from flat comments
  const buildTree = (comments: Comment[]): Comment[] => {
    const map = new Map<number, Comment>();
    const roots: Comment[] = [];

    // First pass: create map of all comments
    comments.forEach((comment) => {
      map.set(comment.id, { ...comment, replies: [] });
    });

    // Second pass: build tree
    comments.forEach((comment) => {
      const node = map.get(comment.id)!;
      if (comment.parent_id) {
        const parent = map.get(comment.parent_id);
        if (parent) {
          parent.replies = parent.replies || [];
          parent.replies.push(node);
        } else {
          // Orphaned reply, treat as root
          roots.push(node);
        }
      } else {
        roots.push(node);
      }
    });

    // Sort by creation date (newest first for roots, oldest first for replies)
    const sortByDate = (a: Comment, b: Comment) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime();

    roots.sort(sortByDate);

    // Sort replies by oldest first
    const sortReplies = (comment: Comment) => {
      if (comment.replies && comment.replies.length > 0) {
        comment.replies.sort(
          (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
        comment.replies.forEach(sortReplies);
      }
    };

    roots.forEach(sortReplies);

    return roots;
  };

  const tree = buildTree(comments);

  if (tree.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-violet-300/50">No comments yet. Be the first to comment!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tree.map((comment) => (
        <CommentCard
          key={comment.id}
          comment={comment}
          onEdit={onEdit}
          onDelete={onDelete}
          onReply={onReply}
          isUpdating={isUpdating}
          isDeleting={isDeleting}
        />
      ))}
    </div>
  );
};
