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
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <AlertCircle className="w-12 h-12 text-destructive mb-4" />
        <h3 className="text-lg font-semibold mb-2">Erreur de chargement</h3>
        <p className="text-sm text-muted-foreground">
          Impossible de charger les mots-clés
        </p>
      </div>
    );
  }

  const selectedKeyword = keywords?.find((k) => k.id === keywordModal.keywordId);

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold">Mots-clés</h2>
          <p className="text-sm text-muted-foreground">
            Gérez les mots-clés qui définissent vos intérêts
          </p>
        </div>
        <Button onClick={() => openKeywordModal('create')}>
          <Plus className="w-4 h-4 mr-2" />
          Nouveau mot-clé
        </Button>
      </div>

      {/* Table */}
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Mot-clé</TableHead>
              <TableHead>Catégorie</TableHead>
              <TableHead>Importance</TableHead>
              <TableHead>Statut</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {keywords?.map((keyword) => (
              <TableRow key={keyword.id}>
                <TableCell className="font-medium">{keyword.keyword}</TableCell>
                <TableCell>
                  <Badge variant="secondary">{keyword.category}</Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className={`w-2 h-2 rounded-full ${
                          i < keyword.weight ? 'bg-primary' : 'bg-muted'
                        }`}
                      />
                    ))}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant={keyword.is_active ? 'default' : 'outline'}>
                    {keyword.is_active ? 'Actif' : 'Inactif'}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openKeywordModal('edit', keyword.id)}
                    >
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteId(keyword.id)}
                    >
                      <Trash2 className="w-4 h-4 text-destructive" />
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
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {keywordModal.mode === 'create'
                ? 'Nouveau mot-clé'
                : 'Modifier le mot-clé'}
            </DialogTitle>
          </DialogHeader>
          <KeywordForm
            keyword={selectedKeyword}
            onSuccess={closeKeywordModal}
          />
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmer la suppression</AlertDialogTitle>
            <AlertDialogDescription>
              Êtes-vous sûr de vouloir supprimer ce mot-clé ? Cette action est
              irréversible.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (deleteId) {
                  deleteMutation.mutate(deleteId);
                  setDeleteId(null);
                }
              }}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Supprimer
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};
