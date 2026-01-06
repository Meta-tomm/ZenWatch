// frontend/hooks/use-comments.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { commentsApi } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { CreateCommentRequest } from '@/types/auth';

interface UseCommentsOptions {
  articleId?: number;
  videoId?: number;
}

export const useComments = ({ articleId, videoId }: UseCommentsOptions) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const queryKey = articleId
    ? ['comments', 'article', articleId]
    : ['comments', 'video', videoId];

  const query = useQuery({
    queryKey,
    queryFn: () => {
      if (articleId) return commentsApi.getForArticle(articleId);
      if (videoId) return commentsApi.getForVideo(videoId);
      return Promise.resolve([]);
    },
    enabled: !!(articleId || videoId),
  });

  const createMutation = useMutation({
    mutationFn: (data: CreateCommentRequest) => commentsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      toast({
        title: 'Comment posted',
        description: 'Your comment has been added',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Could not post comment',
        variant: 'destructive',
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, content }: { id: number; content: string }) =>
      commentsApi.update(id, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      toast({
        title: 'Comment updated',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Could not update comment',
        variant: 'destructive',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => commentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      toast({
        title: 'Comment deleted',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Could not delete comment',
        variant: 'destructive',
      });
    },
  });

  return {
    comments: query.data ?? [],
    isLoading: query.isLoading,
    error: query.error,
    createComment: createMutation.mutate,
    updateComment: updateMutation.mutate,
    deleteComment: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
};
