'use client';

import { useState } from 'react';
import { useKeywords, useDeleteKeyword } from '@/hooks/use-keywords';
import { useModalsStore } from '@/store/modals-store';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { KeywordForm } from './KeywordForm';
import { Plus, Pencil, Trash2, AlertCircle } from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

export const KeywordManager = () => {
  const { data: keywords, isLoading, isError } = useKeywords();
  const deleteMutation = useDeleteKeyword();
  const { keywordModal, openKeywordModal, closeKeywordModal } = useModalsStore();
  const [deleteId, setDeleteId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-black/50 backdrop-blur-sm border border-red-500/30 rounded-lg">
        <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
        <h3 className="text-lg font-semibold mb-2 text-red-400">Erreur de chargement</h3>
        <p className="text-sm text-gold/70">
          Impossible de charger les mots-clés
        </p>
      </div>
    );
  }

  const selectedKeyword = keywords?.find((k) => k.id === keywordModal.keywordId);

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gold">Mots-clés</h2>
          <p className="text-sm text-gold/70">
            Gérez les mots-clés qui définissent vos intérêts
          </p>
        </div>
        <Button
          onClick={() => openKeywordModal('create')}
          className="bg-gold/20 border border-gold/50 text-gold hover:bg-gold/30"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nouveau mot-clé
        </Button>
      </div>

      {/* Table */}
      <div className="bg-black/50 backdrop-blur-sm border border-gold/30 rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-gold/30 hover:bg-gold/10">
              <TableHead className="text-gold">Mot-clé</TableHead>
              <TableHead className="text-gold">Catégorie</TableHead>
              <TableHead className="text-gold">Importance</TableHead>
              <TableHead className="text-gold">Statut</TableHead>
              <TableHead className="text-right text-gold">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {keywords?.map((keyword) => (
              <TableRow
                key={keyword.id}
                className="border-gold/20 hover:bg-gold/5"
              >
                <TableCell className="font-medium text-gold/90">
                  {keyword.keyword}
                </TableCell>
                <TableCell>
                  <Badge
                    variant="secondary"
                    className="bg-zinc-900/50 text-gold border-gold/30"
                  >
                    {keyword.category}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className={`w-2 h-2 rounded-full ${
                          i < keyword.weight
                            ? 'bg-gold-light shadow-[0_0_5px_rgba(255,230,0,0.5)]'
                            : 'bg-zinc-900/30'
                        }`}
                      />
                    ))}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge
                    variant={keyword.is_active ? 'default' : 'outline'}
                    className={
                      keyword.is_active
                        ? 'bg-gold-dark/20 text-gold-dark border-gold-dark/50'
                        : 'bg-zinc-900/20 text-gold/50 border-gold/30'
                    }
                  >
                    {keyword.is_active ? 'Actif' : 'Inactif'}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openKeywordModal('edit', keyword.id)}
                      className="hover:bg-gold/20 hover:text-gold"
                    >
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteId(keyword.id)}
                      className="hover:bg-red-500/20 hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Create/Edit Modal */}
      <Dialog open={keywordModal.open} onOpenChange={closeKeywordModal}>
        <DialogContent className="bg-black/95 backdrop-blur-sm border-gold/30">
          <DialogHeader>
            <DialogTitle className="text-gold glow-text">
              {keywordModal.mode === 'create'
                ? 'Nouveau mot-clé'
                : 'Modifier le mot-clé'}
            </DialogTitle>
            <DialogDescription className="text-gold/70">
              {keywordModal.mode === 'create'
                ? 'Ajoutez un nouveau mot-clé pour personnaliser votre veille technologique'
                : 'Modifiez les paramètres de ce mot-clé'}
            </DialogDescription>
          </DialogHeader>
          <KeywordForm
            keyword={selectedKeyword}
            onSuccess={closeKeywordModal}
          />
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent className="bg-black/95 backdrop-blur-sm border-red-500/30">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-red-400">
              Confirmer la suppression
            </AlertDialogTitle>
            <AlertDialogDescription className="text-gold/70">
              Êtes-vous sûr de vouloir supprimer ce mot-clé ? Cette action est
              irréversible.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-zinc-900/50 border-gold/30 text-gold hover:bg-zinc-900/70">
              Annuler
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (deleteId) {
                  deleteMutation.mutate(deleteId);
                  setDeleteId(null);
                }
              }}
              className="bg-red-500/20 border border-red-500/50 text-red-400 hover:bg-red-500/30"
            >
              Supprimer
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};
