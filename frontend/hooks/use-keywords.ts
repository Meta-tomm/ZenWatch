import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { keywordsApi } from '@/lib/api-client';
import { toast } from '@/hooks/use-toast';
import type { Keyword } from '@/types';

export const useKeywords = () => {
  return useQuery({
    queryKey: ['keywords'],
    queryFn: keywordsApi.getKeywords,
  });
};

export const useCreateKeyword = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Keyword>) => keywordsApi.createKeyword(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] });
      toast({
        title: "Mot-clé créé",
        description: "Le mot-clé a été ajouté avec succès",
      });
    },
    onError: () => {
      toast({
        title: "Erreur",
        description: "Impossible de créer le mot-clé",
        variant: "destructive",
      });
    },
  });
};

export const useUpdateKeyword = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Keyword> }) =>
      keywordsApi.updateKeyword(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] });
      toast({
        title: "Mot-clé mis à jour",
        description: "Le mot-clé a été modifié avec succès",
      });
    },
  });
};

export const useDeleteKeyword = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => keywordsApi.deleteKeyword(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] });
      toast({
        title: "Mot-clé supprimé",
        description: "Le mot-clé a été supprimé avec succès",
      });
    },
  });
};
