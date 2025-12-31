import { create } from 'zustand';

interface ModalsState {
  articleModal: { open: boolean; articleId: string | null };
  keywordModal: { open: boolean; mode: 'create' | 'edit'; keywordId: string | null };
  noteModal: { open: boolean; articleId: string | null };

  openArticleModal: (id: string) => void;
  closeArticleModal: () => void;
  openKeywordModal: (mode: 'create' | 'edit', id?: string | null) => void;
  closeKeywordModal: () => void;
  openNoteModal: (articleId: string) => void;
  closeNoteModal: () => void;
}

export const useModalsStore = create<ModalsState>((set) => ({
  articleModal: { open: false, articleId: null },
  keywordModal: { open: false, mode: 'create', keywordId: null },
  noteModal: { open: false, articleId: null },

  openArticleModal: (id) =>
    set({ articleModal: { open: true, articleId: id } }),

  closeArticleModal: () =>
    set({ articleModal: { open: false, articleId: null } }),

  openKeywordModal: (mode, id = null) =>
    set({ keywordModal: { open: true, mode, keywordId: id } }),

  closeKeywordModal: () =>
    set({ keywordModal: { open: false, mode: 'create', keywordId: null } }),

  openNoteModal: (articleId) =>
    set({ noteModal: { open: true, articleId } }),

  closeNoteModal: () =>
    set({ noteModal: { open: false, articleId: null } }),
}));
