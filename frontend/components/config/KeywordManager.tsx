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
      <div className="flex flex-col items-center justify-center p-8 text-center bg-anthracite-800/50 backdrop-blur-sm border border-red-500/30 rounded-lg">
        <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
        <h3 className="text-lg font-semibold mb-2 text-red-400">Loading error</h3>
        <p className="text-sm text-muted-foreground">
          Unable to load keywords
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
          <h2 className="text-2xl font-bold text-violet-light">Keywords</h2>
          <p className="text-sm text-muted-foreground">
            Manage keywords that define your interests
          </p>
        </div>
        <Button
          onClick={() => openKeywordModal('create')}
          className="bg-violet/20 border border-violet/50 text-violet-light hover:bg-violet/30"
        >
          <Plus className="w-4 h-4 mr-2" />
          New keyword
        </Button>
      </div>

      {/* Table */}
      <div className="bg-anthracite-800/50 backdrop-blur-sm border border-violet/20 rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-violet/20 hover:bg-violet/10">
              <TableHead className="text-violet-light">Keyword</TableHead>
              <TableHead className="text-violet-light">Category</TableHead>
              <TableHead className="text-violet-light">Weight</TableHead>
              <TableHead className="text-violet-light">Status</TableHead>
              <TableHead className="text-right text-violet-light">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {keywords?.map((keyword) => (
              <TableRow
                key={keyword.id}
                className="border-violet/10 hover:bg-violet/5"
              >
                <TableCell className="font-medium text-foreground">
                  {keyword.keyword}
                </TableCell>
                <TableCell>
                  <Badge
                    variant="secondary"
                    className="bg-anthracite-700/50 text-violet-light border-violet/30"
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
                            ? 'bg-violet shadow-[0_0_5px_rgba(139,92,246,0.5)]'
                            : 'bg-anthracite-700/50'
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
                        ? 'bg-violet/20 text-violet-light border-violet/50'
                        : 'bg-anthracite-700/20 text-muted-foreground border-violet/20'
                    }
                  >
                    {keyword.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openKeywordModal('edit', keyword.id)}
                      className="hover:bg-violet/20 hover:text-violet-light"
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
        <DialogContent className="bg-anthracite-900/95 backdrop-blur-sm border-violet/30">
          <DialogHeader>
            <DialogTitle className="text-violet-light">
              {keywordModal.mode === 'create'
                ? 'New keyword'
                : 'Edit keyword'}
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              {keywordModal.mode === 'create'
                ? 'Add a new keyword to customize your tech watch'
                : 'Modify keyword settings'}
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
        <AlertDialogContent className="bg-anthracite-900/95 backdrop-blur-sm border-red-500/30">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-red-400">
              Confirm deletion
            </AlertDialogTitle>
            <AlertDialogDescription className="text-muted-foreground">
              Are you sure you want to delete this keyword? This action is
              irreversible.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-anthracite-800/50 border-violet/30 text-foreground hover:bg-anthracite-700/50">
              Cancel
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
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};
