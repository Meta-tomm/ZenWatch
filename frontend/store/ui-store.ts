import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Theme } from '@/types';

interface UIState {
  sidebarCollapsed: boolean;
  theme: Theme;
  activeFilters: {
    search: string;
    categories: string[];
    sources: string[];
    sort: 'score' | 'date' | 'popularity';
    timeRange: 'all' | '24h' | '7d' | '30d';
  };
  videoFilters: {
    search: string;
    categories: string[];
    sort: 'score' | 'date' | 'popularity';
    timeRange: 'all' | '24h' | '7d' | '30d';
  };

  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: Theme) => void;
  setFilters: (filters: Partial<UIState['activeFilters']>) => void;
  clearFilters: () => void;
  setVideoFilters: (filters: Partial<UIState['videoFilters']>) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      theme: 'light',
      activeFilters: {
        search: '',
        categories: [],
        sources: [],
        sort: 'score',
        timeRange: 'all',
      },
      videoFilters: {
        search: '',
        categories: [],
        sort: 'score',
        timeRange: 'all',
      },

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      setSidebarCollapsed: (collapsed) =>
        set({ sidebarCollapsed: collapsed }),

      setTheme: (theme) => {
        set({ theme });
        // Update DOM
        if (theme === 'dark') {
          document.documentElement.classList.add('dark');
          document.documentElement.removeAttribute('data-theme');
        } else if (theme === 'zenwatch') {
          document.documentElement.classList.remove('dark');
          document.documentElement.setAttribute('data-theme', 'zenwatch');
        } else {
          document.documentElement.classList.remove('dark');
          document.documentElement.removeAttribute('data-theme');
        }
      },

      setFilters: (filters) =>
        set((state) => ({
          activeFilters: { ...state.activeFilters, ...filters },
        })),

      clearFilters: () =>
        set({
          activeFilters: {
            search: '',
            categories: [],
            sources: [],
            sort: 'score',
            timeRange: 'all',
          },
        }),

      setVideoFilters: (filters) =>
        set((state) => ({
          videoFilters: { ...state.videoFilters, ...filters },
        })),
    }),
    {
      name: 'zenwatch-ui-store',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
);
