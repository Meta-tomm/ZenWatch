'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { commentsApi } from '@/lib/api-client';
import type { CommentCreate, CommentUpdate } from '@/types/auth';

type ContentType = 'article' | 'video';

export const useComments = (contentType: ContentType, contentId: number) => {
  const queryClient = useQueryClient();
  const queryKey = ['comments', contentType, contentId];

  const { data: comments = [], isLoading, error } = useQuery({
    queryKey,
    queryFn: () =>
      contentType === 'article'
        ? commentsApi.getForArticle(contentId)
        : commentsApi.getForVideo(contentId),
    enabled: !!contentId,
  });

  const createMutation = useMutation({
    mutationFn: (data: CommentCreate) => commentsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: CommentUpdate }) =>
      commentsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => commentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  });

  const addComment = (content: string, parentId?: number) => {
    const data: CommentCreate = {
      content,
      parent_id: parentId,
      ...(contentType === 'article' ? { article_id: contentId } : { video_id: contentId }),
    };
    createMutation.mutate(data);
  };

  const editComment = (id: number, content: string) => {
    updateMutation.mutate({ id, data: { content } });
  };

  const removeComment = (id: number) => {
    deleteMutation.mutate(id);
  };

  return {
    comments,
    isLoading,
    error,
    addComment,
    editComment,
    removeComment,
    isAdding: createMutation.isPending,
    isEditing: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
};
