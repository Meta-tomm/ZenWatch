# Frontend Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implémenter un dashboard Next.js 14 premium pour TechWatch avec feed d'articles, configuration, analytics Power BI, et optimisations mobile.

**Architecture:** Next.js 14 App Router, TanStack Query (server state) + Zustand (UI state), shadcn/ui components, Framer Motion animations, react-virtuoso infinite scroll, thèmes multiples avec CSS variables.

**Tech Stack:** Next.js 14, React 18, TypeScript, TailwindCSS, shadcn/ui, TanStack Query, Zustand, Framer Motion, axios, Zod, React Hook Form, react-virtuoso, powerbi-client-react

---

## Task 1: Next.js Setup et Configuration de Base

**Files:**
- Verify: `frontend/package.json`
- Verify: `frontend/tailwind.config.ts`
- Create: `frontend/app/globals.css`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`

**Step 1: Vérifier les dépendances**

```bash
cd frontend
cat package.json
```

Expected: Toutes les dépendances sont déjà installées

**Step 2: Installer les dépendances si nécessaire**

```bash
npm install
```

**Step 3: Créer globals.css avec CSS variables pour thèmes**

Create: `frontend/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }

  [data-theme="techwatch"] {
    --background: 220 25% 10%;
    --foreground: 210 40% 98%;
    --card: 220 20% 15%;
    --card-foreground: 210 40% 98%;
    --popover: 220 20% 15%;
    --popover-foreground: 210 40% 98%;
    --primary: 200 100% 50%;
    --primary-foreground: 220 25% 10%;
    --secondary: 220 15% 25%;
    --secondary-foreground: 210 40% 98%;
    --muted: 220 15% 20%;
    --muted-foreground: 215 20% 65%;
    --accent: 270 80% 60%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 210 40% 98%;
    --border: 220 20% 20%;
    --input: 220 20% 18%;
    --ring: 200 100% 50%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

**Step 4: Créer layout.tsx minimal**

Create: `frontend/app/layout.tsx`

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TechWatch - Veille Technologique Intelligente",
  description: "Plateforme de veille tech automatisée",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

**Step 5: Créer page.tsx temporaire**

Create: `frontend/app/page.tsx`

```typescript
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">TechWatch Dashboard</h1>
      <p className="mt-4 text-muted-foreground">Coming soon...</p>
    </main>
  );
}
```

**Step 6: Tester le serveur dev**

```bash
npm run dev
```

Expected: Server runs on http://localhost:3000, page loads with "TechWatch Dashboard"

**Step 7: Commit**

```bash
git add frontend/app/
git commit -m "feat(frontend): setup Next.js 14 with TailwindCSS and theme variables"
```

---

## Task 2: shadcn/ui Components Installation

**Files:**
- Create: `frontend/components/ui/*.tsx`
- Modify: `frontend/components.json`

**Step 1: Initialiser shadcn/ui**

```bash
cd frontend
npx shadcn-ui@latest init
```

Select:
- TypeScript: Yes
- Style: Default
- Base color: Slate
- CSS variables: Yes
- tailwind.config: Yes
- components: @/components
- utils: @/lib/utils

**Step 2: Installer les composants de base**

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add input
npx shadcn-ui@latest add select
npx shadcn-ui@latest add switch
npx shadcn-ui@latest add slider
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add sheet
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add accordion
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add popover
npx shadcn-ui@latest add scroll-area
```

**Step 3: Vérifier les composants créés**

```bash
ls -la components/ui/
```

Expected: Tous les composants listés sont présents

**Step 4: Commit**

```bash
git add components/ui/ lib/ components.json
git commit -m "feat(frontend): install shadcn/ui components"
```

---

## Task 3: Types TypeScript

**Files:**
- Create: `frontend/types/index.ts`

**Step 1: Créer types de base**

```typescript
// frontend/types/index.ts

export interface Article {
  id: string;
  title: string;
  url: string;
  content?: string;
  summary?: string;
  author?: string;
  published_at: string;
  scraped_at?: string;
  score: number;
  category: string;
  tags: string[];
  language?: string;
  read_time_minutes?: number;
  upvotes: number;
  comments_count: number;
  is_read: boolean;
  is_favorite: boolean;
  is_archived: boolean;
  source_type: string;
  created_at: string;
  updated_at?: string;
}

export interface Keyword {
  id: string;
  keyword: string;
  category: string;
  weight: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Source {
  id: string;
  name: string;
  type: string;
  base_url?: string;
  is_active: boolean;
  scrape_frequency_hours: number;
  last_scraped_at?: string;
  config: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface UserConfig {
  id: string;
  email: string;
  daily_digest_enabled: boolean;
  digest_time?: string;
  min_score_threshold: number;
  preferred_categories: string[];
  email_frequency: 'daily' | 'weekly';
  created_at: string;
  updated_at?: string;
}

export interface ArticleFilters {
  search?: string;
  categories?: string[];
  sources?: string[];
  sort?: 'score' | 'date' | 'popularity';
  minScore?: number;
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  hasMore: boolean;
}

export type Theme = 'light' | 'dark' | 'techwatch';
```

**Step 2: Commit**

```bash
git add types/
git commit -m "feat(frontend): add TypeScript types definitions"
```

---

## Task 4: API Client avec Axios

**Files:**
- Create: `frontend/lib/api-client.ts`
- Create: `frontend/.env.local.example`

**Step 1: Créer .env.local.example**

```bash
# frontend/.env.local.example
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_POWERBI_EMBED_URL=
NEXT_PUBLIC_POWERBI_REPORT_ID=
```

**Step 2: Créer API client**

Create: `frontend/lib/api-client.ts`

```typescript
import axios from 'axios';
import type { Article, Keyword, Source, UserConfig, ArticleFilters, PaginatedResponse } from '@/types';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Articles API
export const articlesApi = {
  getArticles: async (params: ArticleFilters): Promise<PaginatedResponse<Article>> => {
    const response = await apiClient.get('/articles', { params });
    return response.data;
  },

  toggleFavorite: async (id: string): Promise<Article> => {
    const response = await apiClient.patch(`/articles/${id}/favorite`);
    return response.data;
  },

  markRead: async (id: string): Promise<Article> => {
    const response = await apiClient.patch(`/articles/${id}/read`);
    return response.data;
  },

  archive: async (id: string): Promise<Article> => {
    const response = await apiClient.patch(`/articles/${id}/archive`);
    return response.data;
  },

  addNote: async (id: string, note: string): Promise<Article> => {
    const response = await apiClient.post(`/articles/${id}/notes`, { note });
    return response.data;
  },
};

// Keywords API
export const keywordsApi = {
  getKeywords: async (): Promise<Keyword[]> => {
    const response = await apiClient.get('/keywords');
    return response.data;
  },

  createKeyword: async (data: Partial<Keyword>): Promise<Keyword> => {
    const response = await apiClient.post('/keywords', data);
    return response.data;
  },

  updateKeyword: async (id: string, data: Partial<Keyword>): Promise<Keyword> => {
    const response = await apiClient.put(`/keywords/${id}`, data);
    return response.data;
  },

  deleteKeyword: async (id: string): Promise<void> => {
    await apiClient.delete(`/keywords/${id}`);
  },
};

// Sources API
export const sourcesApi = {
  getSources: async (): Promise<Source[]> => {
    const response = await apiClient.get('/sources');
    return response.data;
  },

  updateSource: async (id: string, data: Partial<Source>): Promise<Source> => {
    const response = await apiClient.put(`/sources/${id}`, data);
    return response.data;
  },

  triggerScraping: async (sources?: string[]): Promise<{ task_id: string }> => {
    const response = await apiClient.post('/scraping/trigger', { sources });
    return response.data;
  },
};

// User Config API
export const userConfigApi = {
  getConfig: async (): Promise<UserConfig> => {
    const response = await apiClient.get('/user/config');
    return response.data;
  },

  updateConfig: async (data: Partial<UserConfig>): Promise<UserConfig> => {
    const response = await apiClient.put('/user/config', data);
    return response.data;
  },
};
```

**Step 3: Commit**

```bash
git add lib/api-client.ts .env.local.example
git commit -m "feat(frontend): add API client with axios"
```

---

## Task 5: Zustand Stores

**Files:**
- Create: `frontend/store/ui-store.ts`
- Create: `frontend/store/modals-store.ts`

**Step 1: Créer UI Store**

Create: `frontend/store/ui-store.ts`

```typescript
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
  };

  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: Theme) => void;
  setFilters: (filters: Partial<UIState['activeFilters']>) => void;
  clearFilters: () => void;
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
        } else if (theme === 'techwatch') {
          document.documentElement.classList.remove('dark');
          document.documentElement.setAttribute('data-theme', 'techwatch');
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
          },
        }),
    }),
    {
      name: 'techwatch-ui-store',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
);
```

**Step 2: Créer Modals Store**

Create: `frontend/store/modals-store.ts`

```typescript
import { create } from 'zustand';

interface ModalsState {
  articleModal: { open: boolean; articleId: string | null };
  keywordModal: { open: boolean; mode: 'create' | 'edit'; keywordId: string | null };
  noteModal: { open: boolean; articleId: string | null };

  openArticleModal: (id: string) => void;
  closeArticleModal: () => void;
  openKeywordModal: (mode: 'create' | 'edit', id?: string) => void;
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
```

**Step 3: Commit**

```bash
git add store/
git commit -m "feat(frontend): add Zustand stores for UI and modals state"
```

---

## Task 6: TanStack Query Providers

**Files:**
- Create: `frontend/providers/query-provider.tsx`
- Modify: `frontend/app/layout.tsx`

**Step 1: Créer Query Provider**

Create: `frontend/providers/query-provider.tsx`

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 2 * 60 * 1000, // 2 minutes
            refetchOnWindowFocus: true,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

**Step 2: Créer Theme Provider**

Create: `frontend/providers/theme-provider.tsx`

```typescript
'use client';

import { useEffect } from 'react';
import { useUIStore } from '@/store/ui-store';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);

  useEffect(() => {
    // Apply theme on mount
    setTheme(theme);
  }, [theme, setTheme]);

  return <>{children}</>;
}
```

**Step 3: Mettre à jour layout.tsx avec providers**

Modify: `frontend/app/layout.tsx`

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";
import { ThemeProvider } from "@/providers/theme-provider";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TechWatch - Veille Technologique Intelligente",
  description: "Plateforme de veille tech automatisée",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={inter.className}>
        <QueryProvider>
          <ThemeProvider>
            {children}
            <Toaster />
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
```

**Step 4: Installer le composant toaster**

```bash
npx shadcn-ui@latest add toaster
```

**Step 5: Commit**

```bash
git add providers/ app/layout.tsx components/ui/toaster.tsx
git commit -m "feat(frontend): add TanStack Query and Theme providers"
```

---

## Task 7: TanStack Query Hooks

**Files:**
- Create: `frontend/hooks/use-articles.ts`
- Create: `frontend/hooks/use-toggle-favorite.ts`
- Create: `frontend/hooks/use-keywords.ts`

**Step 1: Créer useArticles hook**

Create: `frontend/hooks/use-articles.ts`

```typescript
import { useInfiniteQuery } from '@tanstack/react-query';
import { articlesApi } from '@/lib/api-client';
import type { ArticleFilters } from '@/types';

export const useArticles = (filters: ArticleFilters) => {
  return useInfiniteQuery({
    queryKey: ['articles', filters],
    queryFn: async ({ pageParam = 0 }) => {
      const response = await articlesApi.getArticles({
        ...filters,
        offset: pageParam,
        limit: 50,
      });
      return response;
    },
    getNextPageParam: (lastPage, allPages) => {
      return lastPage.hasMore ? allPages.length * 50 : undefined;
    },
    initialPageParam: 0,
  });
};
```

**Step 2: Créer useToggleFavorite hook (optimistic)**

Create: `frontend/hooks/use-toggle-favorite.ts`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { articlesApi } from '@/lib/api-client';
import { toast } from '@/components/ui/use-toast';
import type { Article } from '@/types';

export const useToggleFavorite = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => articlesApi.toggleFavorite(articleId),

    onMutate: async (articleId) => {
      await queryClient.cancelQueries({ queryKey: ['articles'] });

      const previousData = queryClient.getQueryData(['articles']);

      queryClient.setQueriesData<any>({ queryKey: ['articles'] }, (old) => {
        if (!old) return old;
        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            data: page.data.map((article: Article) =>
              article.id === articleId
                ? { ...article, is_favorite: !article.is_favorite }
                : article
            ),
          })),
        };
      });

      return { previousData };
    },

    onError: (err, variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(['articles'], context.previousData);
      }
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour les favoris",
        variant: "destructive",
      });
    },

    onSuccess: () => {
      toast({
        title: "Favoris mis à jour",
        description: "L'article a été ajouté/retiré des favoris",
      });
    },
  });
};
```

**Step 3: Créer useKeywords hook**

Create: `frontend/hooks/use-keywords.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { keywordsApi } from '@/lib/api-client';
import { toast } from '@/components/ui/use-toast';
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
```

**Step 4: Commit**

```bash
git add hooks/
git commit -m "feat(frontend): add TanStack Query hooks for articles and keywords"
```

---

## Task 8: Sidebar Component (Desktop/Tablet)

**Files:**
- Create: `frontend/components/layout/Sidebar.tsx`
- Create: `frontend/components/layout/NavLink.tsx`

**Step 1: Créer NavLink component**

Create: `frontend/components/layout/NavLink.tsx`

```typescript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface NavLinkProps {
  href: string;
  icon: LucideIcon;
  label: string;
  collapsed?: boolean;
}

export const NavLink = ({ href, icon: Icon, label, collapsed }: NavLinkProps) => {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link
      href={href}
      className={cn(
        'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
        'hover:bg-accent hover:text-accent-foreground',
        isActive && 'bg-accent text-accent-foreground font-medium',
        collapsed && 'justify-center'
      )}
    >
      <Icon className="w-5 h-5 shrink-0" />
      {!collapsed && <span>{label}</span>}
    </Link>
  );
};
```

**Step 2: Créer Sidebar component**

Create: `frontend/components/layout/Sidebar.tsx`

```typescript
'use client';

import { useUIStore } from '@/store/ui-store';
import { Button } from '@/components/ui/button';
import { NavLink } from './NavLink';
import { Home, Settings, BarChart3, ChevronLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', icon: Home, label: 'Feed' },
  { href: '/config', icon: Settings, label: 'Configuration' },
  { href: '/analytics', icon: BarChart3, label: 'Analytics' },
];

export const Sidebar = () => {
  const collapsed = useUIStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);

  return (
    <aside
      className={cn(
        'hidden md:flex flex-col border-r bg-card transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        {!collapsed && (
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            TechWatch
          </h1>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleSidebar}
          className={cn(collapsed && 'mx-auto')}
        >
          <ChevronLeft
            className={cn(
              'w-4 h-4 transition-transform',
              collapsed && 'rotate-180'
            )}
          />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            href={item.href}
            icon={item.icon}
            label={item.label}
            collapsed={collapsed}
          />
        ))}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="p-4 border-t text-xs text-muted-foreground">
          TechWatch v1.0.0
        </div>
      )}
    </aside>
  );
};
```

**Step 3: Tester le composant**

```bash
npm run dev
```

Expected: Sidebar s'affiche sur desktop, collapse/expand fonctionne

**Step 4: Commit**

```bash
git add components/layout/
git commit -m "feat(frontend): add Sidebar and NavLink components"
```

---

## Task 9: Mobile Navigation (BottomNav + TopBar)

**Files:**
- Create: `frontend/components/layout/BottomNav.tsx`
- Create: `frontend/components/layout/TopBar.tsx`

**Step 1: Créer BottomNav**

Create: `frontend/components/layout/BottomNav.tsx`

```typescript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Settings, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', icon: Home, label: 'Feed' },
  { href: '/config', icon: Settings, label: 'Config' },
  { href: '/analytics', icon: BarChart3, label: 'Analytics' },
];

export const BottomNav = () => {
  const pathname = usePathname();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-card border-t">
      <div className="flex items-center justify-around h-16">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex flex-col items-center justify-center gap-1 flex-1 h-full transition-colors',
                isActive
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};
```

**Step 2: Créer TopBar**

Create: `frontend/components/layout/TopBar.tsx`

```typescript
'use client';

import { ThemeToggle } from '@/components/ThemeToggle';
import { useUIStore } from '@/store/ui-store';
import { Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const TopBar = () => {
  return (
    <header className="md:hidden sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <div className="flex items-center justify-between h-14 px-4">
        <h1 className="text-lg font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          TechWatch
        </h1>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <Search className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Filter className="w-4 h-4" />
          </Button>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};
```

**Step 3: Commit**

```bash
git add components/layout/BottomNav.tsx components/layout/TopBar.tsx
git commit -m "feat(frontend): add mobile BottomNav and TopBar"
```

---

## Task 10: ThemeToggle Component

**Files:**
- Create: `frontend/components/ThemeToggle.tsx`

**Step 1: Créer ThemeToggle**

Create: `frontend/components/ThemeToggle.tsx`

```typescript
'use client';

import { useUIStore } from '@/store/ui-store';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Sun, Moon, Palette } from 'lucide-react';
import type { Theme } from '@/types';

export const ThemeToggle = () => {
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);

  const Icon = theme === 'light' ? Sun : theme === 'dark' ? Moon : Palette;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm">
          <Icon className="w-4 h-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme('light')}>
          <Sun className="w-4 h-4 mr-2" />
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('dark')}>
          <Moon className="w-4 h-4 mr-2" />
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('techwatch')}>
          <Palette className="w-4 h-4 mr-2" />
          TechWatch
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
```

**Step 2: Commit**

```bash
git add components/ThemeToggle.tsx
git commit -m "feat(frontend): add ThemeToggle component"
```

---

## Task 11: Main Layout Assembly

**Files:**
- Modify: `frontend/app/layout.tsx`
- Create: `frontend/components/layout/MainLayout.tsx`

**Step 1: Créer MainLayout**

Create: `frontend/components/layout/MainLayout.tsx`

```typescript
'use client';

import { Sidebar } from './Sidebar';
import { BottomNav } from './BottomNav';
import { TopBar } from './TopBar';

export const MainLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar />

        <main className="flex-1 overflow-y-auto pb-16 md:pb-0">
          {children}
        </main>

        <BottomNav />
      </div>
    </div>
  );
};
```

**Step 2: Mettre à jour layout.tsx**

Modify: `frontend/app/layout.tsx`

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";
import { ThemeProvider } from "@/providers/theme-provider";
import { Toaster } from "@/components/ui/toaster";
import { MainLayout } from "@/components/layout/MainLayout";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TechWatch - Veille Technologique Intelligente",
  description: "Plateforme de veille tech automatisée",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={inter.className}>
        <QueryProvider>
          <ThemeProvider>
            <MainLayout>{children}</MainLayout>
            <Toaster />
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
```

**Step 3: Tester le layout**

```bash
npm run dev
```

Expected: Layout complet avec Sidebar (desktop), TopBar + BottomNav (mobile)

**Step 4: Commit**

```bash
git add components/layout/MainLayout.tsx app/layout.tsx
git commit -m "feat(frontend): assemble complete main layout"
```

---

## Task 12: FilterBar Component

**Files:**
- Create: `frontend/components/feed/FilterBar.tsx`

**Step 1: Créer FilterBar**

Create: `frontend/components/feed/FilterBar.tsx`

```typescript
'use client';

import { useUIStore } from '@/store/ui-store';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Search, X } from 'lucide-react';

const CATEGORIES = [
  'healthtech',
  'blockchain',
  'dev',
  'ai',
  'cloud',
  'security',
];

const SOURCES = ['reddit', 'hackernews', 'devto', 'github', 'medium'];

export const FilterBar = () => {
  const { activeFilters, setFilters, clearFilters } = useUIStore();

  return (
    <div className="sticky top-0 z-30 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b p-4">
      {/* Search */}
      <div className="flex items-center gap-2 mb-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher..."
            value={activeFilters.search}
            onChange={(e) => setFilters({ search: e.target.value })}
            className="pl-9"
          />
        </div>

        {/* Sort */}
        <Select
          value={activeFilters.sort}
          onValueChange={(value) =>
            setFilters({ sort: value as 'score' | 'date' | 'popularity' })
          }
        >
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="score">Score</SelectItem>
            <SelectItem value="date">Date</SelectItem>
            <SelectItem value="popularity">Popularité</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap gap-2 mb-2">
        {CATEGORIES.map((cat) => {
          const isActive = activeFilters.categories.includes(cat);
          return (
            <Badge
              key={cat}
              variant={isActive ? 'default' : 'outline'}
              className="cursor-pointer hover:bg-primary/10"
              onClick={() => {
                const newCategories = isActive
                  ? activeFilters.categories.filter((c) => c !== cat)
                  : [...activeFilters.categories, cat];
                setFilters({ categories: newCategories });
              }}
            >
              {cat}
            </Badge>
          );
        })}
      </div>

      {/* Active Filters */}
      {(activeFilters.search ||
        activeFilters.categories.length > 0 ||
        activeFilters.sources.length > 0) && (
        <div className="flex items-center gap-2 pt-2 border-t">
          <span className="text-sm text-muted-foreground">Filtres actifs:</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="h-7"
          >
            <X className="w-3 h-3 mr-1" />
            Effacer
          </Button>
        </div>
      )}
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add components/feed/FilterBar.tsx
git commit -m "feat(frontend): add FilterBar with search and category filters"
```

---

## Task 13: ArticleCard Component

**Files:**
- Create: `frontend/components/feed/ArticleCard.tsx`
- Create: `frontend/lib/date-utils.ts`

**Step 1: Créer date utils**

Create: `frontend/lib/date-utils.ts`

```typescript
import { formatDistanceToNow, format } from 'date-fns';
import { fr } from 'date-fns/locale';

export const formatRelativeDate = (date: string) => {
  return formatDistanceToNow(new Date(date), {
    addSuffix: true,
    locale: fr,
  });
};

export const formatDate = (date: string) => {
  return format(new Date(date), 'dd MMM yyyy', { locale: fr });
};
```

**Step 2: Créer ArticleCard**

Create: `frontend/components/feed/ArticleCard.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, ExternalLink, MessageSquare, TrendingUp, BookmarkPlus } from 'lucide-react';
import { useToggleFavorite } from '@/hooks/use-toggle-favorite';
import { formatRelativeDate } from '@/lib/date-utils';
import { cn } from '@/lib/utils';
import type { Article } from '@/types';

interface ArticleCardProps {
  article: Article;
  onOpenModal?: (id: string) => void;
}

export const ArticleCard = ({ article, onOpenModal }: ArticleCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const toggleFavorite = useToggleFavorite();

  const scoreColor = article.score >= 70 ? 'text-green-500' : article.score >= 50 ? 'text-yellow-500' : 'text-muted-foreground';

  return (
    <Card
      className={cn(
        'transition-all hover:shadow-md',
        article.is_read && 'opacity-60'
      )}
    >
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex-1 min-w-0">
            <h3
              className="font-semibold leading-tight mb-1 cursor-pointer hover:text-primary line-clamp-2"
              onClick={() => onOpenModal?.(article.id)}
            >
              {article.title}
            </h3>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="capitalize">{article.source_type}</span>
              <span>•</span>
              <span>{formatRelativeDate(article.published_at)}</span>
              {article.read_time_minutes && (
                <>
                  <span>•</span>
                  <span>{article.read_time_minutes} min</span>
                </>
              )}
            </div>
          </div>

          {/* Score */}
          <div className="flex flex-col items-center shrink-0">
            <div className={cn('text-2xl font-bold', scoreColor)}>
              {article.score.toFixed(0)}
            </div>
            <div className="text-xs text-muted-foreground">score</div>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          <Badge variant="secondary" className="text-xs">
            {article.category}
          </Badge>
          {article.tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>

        {/* Summary */}
        {article.summary && (
          <p
            className={cn(
              'text-sm text-muted-foreground leading-relaxed mb-3',
              !isExpanded && 'line-clamp-2'
            )}
          >
            {article.summary}
          </p>
        )}

        {/* Stats */}
        <div className="flex items-center gap-4 mb-3 text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            {article.upvotes}
          </div>
          <div className="flex items-center gap-1">
            <MessageSquare className="w-3 h-3" />
            {article.comments_count}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between border-t pt-3">
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleFavorite.mutate(article.id)}
            >
              <Star
                className={cn(
                  'w-4 h-4',
                  article.is_favorite && 'fill-yellow-500 text-yellow-500'
                )}
              />
            </Button>
            <Button variant="ghost" size="sm">
              <BookmarkPlus className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex items-center gap-1">
            {article.summary && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? 'Réduire' : 'Voir plus'}
              </Button>
            )}
            <Button variant="ghost" size="sm" asChild>
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
```

**Step 3: Installer date-fns**

```bash
npm install date-fns
```

**Step 4: Commit**

```bash
git add components/feed/ArticleCard.tsx lib/date-utils.ts package.json
git commit -m "feat(frontend): add ArticleCard component with date utilities"
```

---

## Task 14: ArticleFeed with Infinite Scroll

**Files:**
- Create: `frontend/components/feed/ArticleFeed.tsx`

**Step 1: Créer ArticleFeed**

Create: `frontend/components/feed/ArticleFeed.tsx`

```typescript
'use client';

import { useArticles } from '@/hooks/use-articles';
import { useUIStore } from '@/store/ui-store';
import { useModalsStore } from '@/store/modals-store';
import { ArticleCard } from './ArticleCard';
import { Skeleton } from '@/components/ui/skeleton';
import { Virtuoso } from 'react-virtuoso';
import { AlertCircle } from 'lucide-react';

export const ArticleFeed = () => {
  const activeFilters = useUIStore((s) => s.activeFilters);
  const openArticleModal = useModalsStore((s) => s.openArticleModal);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
  } = useArticles({
    search: activeFilters.search,
    categories: activeFilters.categories,
    sources: activeFilters.sources,
    sort: activeFilters.sort,
  });

  const allArticles = data?.pages.flatMap((page) => page.data) ?? [];

  if (isLoading) {
    return (
      <div className="p-4 space-y-4">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-48 w-full" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <AlertCircle className="w-12 h-12 text-destructive mb-4" />
        <h2 className="text-lg font-semibold mb-2">Erreur de chargement</h2>
        <p className="text-sm text-muted-foreground">
          Impossible de charger les articles. Veuillez réessayer.
        </p>
      </div>
    );
  }

  if (allArticles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <h2 className="text-lg font-semibold mb-2">Aucun article trouvé</h2>
        <p className="text-sm text-muted-foreground">
          Essayez de modifier vos filtres ou mots-clés
        </p>
      </div>
    );
  }

  return (
    <Virtuoso
      data={allArticles}
      endReached={() => {
        if (hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      }}
      itemContent={(index, article) => (
        <div className="px-4 py-2">
          <ArticleCard
            article={article}
            onOpenModal={openArticleModal}
          />
        </div>
      )}
      components={{
        Footer: () =>
          isFetchingNextPage ? (
            <div className="p-4">
              <Skeleton className="h-48 w-full" />
            </div>
          ) : null,
      }}
    />
  );
};
```

**Step 2: Installer react-virtuoso**

```bash
npm install react-virtuoso
```

**Step 3: Commit**

```bash
git add components/feed/ArticleFeed.tsx package.json
git commit -m "feat(frontend): add ArticleFeed with infinite scroll virtualization"
```

---

## Task 15: Page Feed Assembly

**Files:**
- Modify: `frontend/app/page.tsx`

**Step 1: Mettre à jour page.tsx**

Modify: `frontend/app/page.tsx`

```typescript
import { FilterBar } from '@/components/feed/FilterBar';
import { ArticleFeed } from '@/components/feed/ArticleFeed';

export default function Home() {
  return (
    <div className="flex flex-col h-full">
      <FilterBar />
      <ArticleFeed />
    </div>
  );
}
```

**Step 2: Tester la page**

```bash
npm run dev
```

Expected: Feed avec filtres, infinite scroll, et cartes d'articles

**Step 3: Commit**

```bash
git add app/page.tsx
git commit -m "feat(frontend): assemble Feed page with filters and articles"
```

---

## Task 16: ArticleModal Component

**Files:**
- Create: `frontend/components/feed/ArticleModal.tsx`
- Modify: `frontend/app/page.tsx`

**Step 1: Créer ArticleModal**

Create: `frontend/components/feed/ArticleModal.tsx`

```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { useModalsStore } from '@/store/modals-store';
import { articlesApi } from '@/lib/api-client';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ExternalLink, Star, BookmarkPlus } from 'lucide-react';
import { formatDate } from '@/lib/date-utils';
import { useToggleFavorite } from '@/hooks/use-toggle-favorite';

export const ArticleModal = () => {
  const { articleModal, closeArticleModal } = useModalsStore();
  const toggleFavorite = useToggleFavorite();

  const { data: article, isLoading } = useQuery({
    queryKey: ['article', articleModal.articleId],
    queryFn: async () => {
      // TODO: Replace with actual API call when backend ready
      // For now, we'll get from cache
      return null;
    },
    enabled: articleModal.open && !!articleModal.articleId,
  });

  return (
    <Dialog open={articleModal.open} onOpenChange={closeArticleModal}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : article ? (
          <>
            <DialogHeader>
              <DialogTitle className="text-2xl leading-tight pr-8">
                {article.title}
              </DialogTitle>
            </DialogHeader>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <span className="capitalize">{article.source_type}</span>
              <span>•</span>
              <span>{formatDate(article.published_at)}</span>
              {article.author && (
                <>
                  <span>•</span>
                  <span>Par {article.author}</span>
                </>
              )}
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2">
              <Badge>{article.category}</Badge>
              {article.tags.map((tag) => (
                <Badge key={tag} variant="outline">
                  {tag}
                </Badge>
              ))}
            </div>

            {/* Score */}
            <div className="flex items-center gap-4 p-4 bg-muted rounded-lg">
              <div>
                <div className="text-3xl font-bold text-primary">
                  {article.score.toFixed(0)}
                </div>
                <div className="text-xs text-muted-foreground">Score</div>
              </div>
              <div className="flex-1 text-sm text-muted-foreground">
                Basé sur vos mots-clés et préférences
              </div>
            </div>

            {/* Summary */}
            {article.summary && (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <h3 className="text-lg font-semibold mb-2">Résumé IA</h3>
                <p className="leading-relaxed">{article.summary}</p>
              </div>
            )}

            {/* Content */}
            {article.content && (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <h3 className="text-lg font-semibold mb-2">Contenu</h3>
                <div
                  className="leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: article.content }}
                />
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-2 pt-4 border-t">
              <Button
                variant="outline"
                onClick={() => toggleFavorite.mutate(article.id)}
              >
                <Star
                  className={
                    article.is_favorite ? 'fill-yellow-500 text-yellow-500' : ''
                  }
                />
                {article.is_favorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
              </Button>
              <Button variant="outline">
                <BookmarkPlus className="w-4 h-4 mr-2" />
                Archiver
              </Button>
              <Button asChild className="ml-auto">
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Lire l'article
                </a>
              </Button>
            </div>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
};
```

**Step 2: Ajouter modal à la page**

Modify: `frontend/app/page.tsx`

```typescript
import { FilterBar } from '@/components/feed/FilterBar';
import { ArticleFeed } from '@/components/feed/ArticleFeed';
import { ArticleModal } from '@/components/feed/ArticleModal';

export default function Home() {
  return (
    <>
      <div className="flex flex-col h-full">
        <FilterBar />
        <ArticleFeed />
      </div>
      <ArticleModal />
    </>
  );
}
```

**Step 3: Commit**

```bash
git add components/feed/ArticleModal.tsx app/page.tsx
git commit -m "feat(frontend): add ArticleModal for detailed article view"
```

---

## Task 17: Configuration Page - Keywords Manager

**Files:**
- Create: `frontend/app/config/page.tsx`
- Create: `frontend/components/config/KeywordManager.tsx`
- Create: `frontend/components/config/KeywordForm.tsx`

**Step 1: Créer KeywordForm**

Create: `frontend/components/config/KeywordForm.tsx`

```typescript
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useCreateKeyword, useUpdateKeyword } from '@/hooks/use-keywords';
import type { Keyword } from '@/types';

const keywordSchema = z.object({
  keyword: z.string().min(2, 'Minimum 2 caractères').max(50),
  category: z.string().min(1, 'Catégorie requise'),
  weight: z.number().min(1).max(5),
});

type KeywordFormData = z.infer<typeof keywordSchema>;

interface KeywordFormProps {
  keyword?: Keyword;
  onSuccess: () => void;
}

const CATEGORIES = [
  'healthtech',
  'blockchain',
  'dev',
  'ai',
  'cloud',
  'security',
];

export const KeywordForm = ({ keyword, onSuccess }: KeywordFormProps) => {
  const createMutation = useCreateKeyword();
  const updateMutation = useUpdateKeyword();

  const form = useForm<KeywordFormData>({
    resolver: zodResolver(keywordSchema),
    defaultValues: {
      keyword: keyword?.keyword ?? '',
      category: keyword?.category ?? 'dev',
      weight: keyword?.weight ?? 3,
    },
  });

  const onSubmit = async (data: KeywordFormData) => {
    try {
      if (keyword) {
        await updateMutation.mutateAsync({ id: keyword.id, data });
      } else {
        await createMutation.mutateAsync(data);
      }
      onSuccess();
    } catch (error) {
      console.error('Error saving keyword:', error);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="keyword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Mot-clé</FormLabel>
              <FormControl>
                <Input placeholder="Ex: FHIR, blockchain..." {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="category"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Catégorie</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {CATEGORIES.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="weight"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Importance: {field.value}/5</FormLabel>
              <FormControl>
                <Slider
                  min={1}
                  max={5}
                  step={1}
                  value={[field.value]}
                  onValueChange={([value]) => field.onChange(value)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex gap-2">
          <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
            {keyword ? 'Mettre à jour' : 'Créer'}
          </Button>
        </div>
      </form>
    </Form>
  );
};
```

**Step 2: Installer react-hook-form et zod resolver**

```bash
npm install react-hook-form @hookform/resolvers/zod
npx shadcn-ui@latest add form
npx shadcn-ui@latest add slider
```

**Step 3: Commit**

```bash
git add components/config/KeywordForm.tsx package.json
git commit -m "feat(frontend): add KeywordForm with validation"
```

---

## Task 18: Keywords Manager Table

**Files:**
- Create: `frontend/components/config/KeywordManager.tsx`

**Step 1: Créer KeywordManager**

Create: `frontend/components/config/KeywordManager.tsx`

```typescript
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
```

**Step 2: Installer composants manquants**

```bash
npx shadcn-ui@latest add table
npx shadcn-ui@latest add alert-dialog
```

**Step 3: Commit**

```bash
git add components/config/KeywordManager.tsx components/ui/
git commit -m "feat(frontend): add KeywordManager with table and modals"
```

---

## Task 19: Configuration Page Assembly

**Files:**
- Create: `frontend/app/config/page.tsx`

**Step 1: Créer config page**

Create: `frontend/app/config/page.tsx`

```typescript
import { KeywordManager } from '@/components/config/KeywordManager';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function ConfigPage() {
  return (
    <div className="container max-w-6xl py-6">
      <Tabs defaultValue="keywords" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="keywords">Mots-clés</TabsTrigger>
          <TabsTrigger value="sources">Sources</TabsTrigger>
          <TabsTrigger value="preferences">Préférences</TabsTrigger>
        </TabsList>

        <TabsContent value="keywords">
          <KeywordManager />
        </TabsContent>

        <TabsContent value="sources">
          <div className="text-center text-muted-foreground py-12">
            Sources management coming soon...
          </div>
        </TabsContent>

        <TabsContent value="preferences">
          <div className="text-center text-muted-foreground py-12">
            User preferences coming soon...
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add app/config/page.tsx
git commit -m "feat(frontend): add Configuration page with Keywords tab"
```

---

## Task 20: Analytics Page with Power BI Placeholder

**Files:**
- Create: `frontend/app/analytics/page.tsx`
- Create: `frontend/components/analytics/PowerBIDashboard.tsx`

**Step 1: Créer PowerBIDashboard placeholder**

Create: `frontend/components/analytics/PowerBIDashboard.tsx`

```typescript
'use client';

import { Card, CardContent } from '@/components/ui/card';
import { BarChart3 } from 'lucide-react';

export const PowerBIDashboard = () => {
  return (
    <Card className="w-full h-full min-h-[600px]">
      <CardContent className="flex flex-col items-center justify-center h-full p-12 text-center">
        <BarChart3 className="w-24 h-24 text-muted-foreground mb-6" />
        <h3 className="text-2xl font-bold mb-2">Power BI Dashboard</h3>
        <p className="text-muted-foreground max-w-md">
          Les dashboards Power BI seront intégrés ici une fois le backend
          configuré avec les embed tokens.
        </p>
        <div className="mt-6 text-xs text-muted-foreground">
          Configuration requise :
          <ul className="list-disc list-inside mt-2 text-left">
            <li>Power BI Workspace ID</li>
            <li>Power BI Report ID</li>
            <li>API endpoint pour embed token</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};
```

**Step 2: Créer analytics page**

Create: `frontend/app/analytics/page.tsx`

```typescript
import { PowerBIDashboard } from '@/components/analytics/PowerBIDashboard';

export default function AnalyticsPage() {
  return (
    <div className="container max-w-7xl py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Analytics</h1>
        <p className="text-muted-foreground">
          Visualisez vos tendances et statistiques de veille
        </p>
      </div>

      <PowerBIDashboard />
    </div>
  );
}
```

**Step 3: Commit**

```bash
git add app/analytics/ components/analytics/
git commit -m "feat(frontend): add Analytics page with Power BI placeholder"
```

---

## Task 21: Framer Motion Animations

**Files:**
- Create: `frontend/lib/motion-variants.ts`
- Modify: `frontend/components/feed/ArticleCard.tsx`

**Step 1: Créer motion variants**

Create: `frontend/lib/motion-variants.ts`

```typescript
import type { Variants } from 'framer-motion';

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const scaleIn: Variants = {
  hidden: { scale: 0.95, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: { duration: 0.2 },
  },
};

export const slideInFromRight: Variants = {
  hidden: { x: 50, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: { duration: 0.3 },
  },
};
```

**Step 2: Ajouter animation à ArticleCard**

Modify: `frontend/components/feed/ArticleCard.tsx` (add at top):

```typescript
'use client';

import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/motion-variants';
// ... existing imports

// Wrap Card with motion.div
export const ArticleCard = ({ article, onOpenModal }: ArticleCardProps) => {
  // ... existing code

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card className={cn(/* ... */)}>
        {/* ... existing content */}
      </Card>
    </motion.div>
  );
};
```

**Step 3: Installer framer-motion**

```bash
npm install framer-motion
```

**Step 4: Commit**

```bash
git add lib/motion-variants.ts components/feed/ArticleCard.tsx package.json
git commit -m "feat(frontend): add Framer Motion animations"
```

---

## Task 22: Responsive Optimizations

**Files:**
- Modify: `frontend/tailwind.config.ts`
- Create: `frontend/components/ui/responsive-dialog.tsx`

**Step 1: Optimiser Tailwind config**

Modify: `frontend/tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      screens: {
        xs: "375px",
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1536px",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
```

**Step 2: Créer ResponsiveDialog**

Create: `frontend/components/ui/responsive-dialog.tsx`

```typescript
'use client';

import * as React from 'react';
import { useMediaQuery } from '@/hooks/use-media-query';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from '@/components/ui/drawer';

interface ResponsiveDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
}

export const ResponsiveDialog = ({
  open,
  onOpenChange,
  title,
  description,
  children,
}: ResponsiveDialogProps) => {
  const isDesktop = useMediaQuery('(min-width: 768px)');

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{title}</DialogTitle>
            {description && <DialogDescription>{description}</DialogDescription>}
          </DialogHeader>
          {children}
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>{title}</DrawerTitle>
          {description && <DrawerDescription>{description}</DrawerDescription>}
        </DrawerHeader>
        <div className="px-4 pb-4">{children}</div>
      </DrawerContent>
    </Drawer>
  );
};
```

**Step 3: Créer useMediaQuery hook**

Create: `frontend/hooks/use-media-query.ts`

```typescript
import { useState, useEffect } from 'react';

export function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    const listener = () => setMatches(media.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [matches, query]);

  return matches;
}
```

**Step 4: Installer drawer**

```bash
npx shadcn-ui@latest add drawer
```

**Step 5: Commit**

```bash
git add tailwind.config.ts components/ui/responsive-dialog.tsx hooks/use-media-query.ts
git commit -m "feat(frontend): add responsive optimizations and ResponsiveDialog"
```

---

## Task 23: Final Testing & Build

**Files:**
- Create: `frontend/.env.local`
- Create: `frontend/README.md`

**Step 1: Créer .env.local**

Create: `frontend/.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_POWERBI_EMBED_URL=
NEXT_PUBLIC_POWERBI_REPORT_ID=
```

**Step 2: Tester build production**

```bash
npm run build
```

Expected: Build réussit sans erreurs TypeScript

**Step 3: Tester prod server**

```bash
npm run start
```

Expected: Application fonctionne en mode production

**Step 4: Créer README**

Create: `frontend/README.md`

```markdown
# TechWatch Frontend

Dashboard Next.js 14 pour la veille technologique.

## Stack

- Next.js 14 (App Router)
- TypeScript
- TailwindCSS + shadcn/ui
- TanStack Query
- Zustand
- Framer Motion
- react-virtuoso

## Dev

\```bash
npm install
npm run dev
\```

## Build

\```bash
npm run build
npm run start
\```

## Features

- ✅ Feed d'articles avec infinite scroll
- ✅ Filtres et recherche
- ✅ Gestion mots-clés
- ✅ Thèmes multiples
- ✅ Responsive mobile/desktop
- ✅ Animations fluides
- ⏳ Power BI integration

## Structure

- `/app` - Pages Next.js
- `/components` - Composants React
- `/hooks` - Custom hooks
- `/lib` - Utilities
- `/store` - Zustand stores
- `/types` - TypeScript types
```

**Step 5: Commit final**

```bash
git add .env.local README.md
git commit -m "feat(frontend): complete frontend implementation with docs"
```

**Step 6: Vérifier tous les tests**

```bash
npm run lint
npm run build
```

Expected: Aucune erreur

---

## Plan Complete

**Total: 23 tasks completed**

**Summary:**
1. ✅ Next.js setup avec TailwindCSS
2. ✅ shadcn/ui components installation
3. ✅ Types TypeScript
4. ✅ API Client
5. ✅ Zustand stores
6. ✅ TanStack Query providers
7. ✅ TanStack Query hooks
8. ✅ Sidebar component
9. ✅ Mobile navigation
10. ✅ Theme toggle
11. ✅ Main layout assembly
12. ✅ Filter bar
13. ✅ Article card
14. ✅ Article feed with infinite scroll
15. ✅ Feed page assembly
16. ✅ Article modal
17. ✅ Keyword form
18. ✅ Keywords manager
19. ✅ Config page
20. ✅ Analytics page
21. ✅ Framer Motion animations
22. ✅ Responsive optimizations
23. ✅ Final testing & build

**Next Steps:**
- Backend API implementation
- Power BI integration
- Unit tests avec Vitest
- E2E tests
- Performance optimizations
