'use client';

import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { MoreHorizontal, Pencil, Trash2, Reply, User } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { CommentForm } from './CommentForm';
import { useCurrentUser } from '@/hooks/use-current-user';
import { cn } from '@/lib/utils';
import type { Comment } from '@/types/auth';

interface CommentCardProps {
  comment: Comment;
  onEdit: (id: number, content: string) => void;
  onDelete: (id: number) => void;
  onReply: (parentId: number, content: string) => void;
  isUpdating?: boolean;
  isDeleting?: boolean;
}

export const CommentCard = ({
  comment,
  onEdit,
  onDelete,
  onReply,
  isUpdating = false,
  isDeleting = false,
}: CommentCardProps) => {
  const { user } = useCurrentUser();
  const [isEditing, setIsEditing] = useState(false);
  const [isReplying, setIsReplying] = useState(false);

  const isOwner = user?.id === comment.user_id;
  const displayUser = comment.user;

  const handleEdit = (content: string) => {
    onEdit(comment.id, content);
    setIsEditing(false);
  };

  const handleReply = (content: string) => {
    onReply(comment.id, content);
    setIsReplying(false);
  };

  const getInitials = (username?: string) => {
    if (!username) return 'U';
    return username.slice(0, 2).toUpperCase();
  };

  if (comment.is_deleted) {
    return (
      <div className="p-3 bg-anthracite-800/50 border border-violet-500/20 rounded-lg">
        <p className="text-violet-300/50 italic text-sm">
          This comment has been deleted
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="p-4 bg-anthracite-800/80 border border-violet-500/30 rounded-lg">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <Avatar className="h-8 w-8">
              {displayUser?.avatar_url && (
                <AvatarImage src={displayUser.avatar_url} alt={displayUser.username} />
              )}
              <AvatarFallback className="bg-violet-600 text-white text-xs">
                {getInitials(displayUser?.username)}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium text-violet-200">
                {displayUser?.username || 'Unknown User'}
              </p>
              <p className="text-xs text-violet-300/50">
                {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
                {comment.updated_at !== comment.created_at && ' (edited)'}
              </p>
            </div>
          </div>

          {isOwner && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0 text-violet-300/70 hover:text-violet-200"
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                className="bg-anthracite-800 border-violet-500/30"
              >
                <DropdownMenuItem
                  onClick={() => setIsEditing(true)}
                  className="text-violet-200 focus:bg-violet-500/20"
                >
                  <Pencil className="mr-2 h-4 w-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => onDelete(comment.id)}
                  className="text-red-400 focus:bg-red-500/20"
                  disabled={isDeleting}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>

        {/* Content */}
        {isEditing ? (
          <CommentForm
            initialValue={comment.content}
            onSubmit={handleEdit}
            onCancel={() => setIsEditing(false)}
            isSubmitting={isUpdating}
            autoFocus
          />
        ) : (
          <p className="text-sm text-violet-100/90 whitespace-pre-wrap">
            {comment.content}
          </p>
        )}

        {/* Actions */}
        {!isEditing && user && (
          <div className="mt-3 pt-3 border-t border-violet-500/20">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsReplying(!isReplying)}
              className="text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20"
            >
              <Reply className="mr-2 h-4 w-4" />
              Reply
            </Button>
          </div>
        )}
      </div>

      {/* Reply form */}
      {isReplying && (
        <div className="ml-8">
          <CommentForm
            placeholder="Write a reply..."
            onSubmit={handleReply}
            onCancel={() => setIsReplying(false)}
            autoFocus
          />
        </div>
      )}

      {/* Replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="ml-8 space-y-3">
          {comment.replies.map((reply) => (
            <CommentCard
              key={reply.id}
              comment={reply}
              onEdit={onEdit}
              onDelete={onDelete}
              onReply={onReply}
              isUpdating={isUpdating}
              isDeleting={isDeleting}
            />
          ))}
        </div>
      )}
    </div>
  );
};
