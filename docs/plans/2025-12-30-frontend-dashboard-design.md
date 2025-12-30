# Design du Frontend Dashboard - TechWatch

**Date**: 2025-12-30
**Version**: 1.0.0
**Auteur**: Tom (Epitech Lyon)
**Status**: Validé

## Vue d'ensemble

Dashboard Next.js 14 moderne et performant pour TechWatch, permettant de consulter, filtrer et gérer les articles scrapés. Interface premium avec navigation sidebar collapsible, thèmes multiples, optimisations mobile avec gestures, et intégration Power BI pour l'analytics.

## Objectifs

- **UX Premium**: Animations fluides, skeleton loading, optimistic updates, gestures intuitives
- **Performance**: Virtualization, infinite scroll, code splitting, bundle <300KB
- **Responsive**: Mobile-first avec gestures natives, tablet optimisé, desktop riche
- **Scalabilité**: Architecture modulaire, composants réutilisables, state management clair

## Décisions de Design

### Pages et Navigation

**Pages principales:**
- **Feed** (`/`) - Flux d'articles avec filtres et recherche
- **Configuration** (`/config`) - Gestion keywords, sources, préférences
- **Analytics** (`/analytics`) - Dashboard Power BI embedded

**Navigation:**
- Desktop/Tablet: **Sidebar collapsible** (280px expanded, 80px collapsed)
- Mobile: **Bottom navigation** (3 items fixes)
- Top bar: Logo, search, user menu, theme toggle

### Layout Articles

**Cards layout** visuellement riche:
- Grille responsive (2 colonnes desktop, 1 colonne mobile)
- Cards spacieuses avec favicon source, titre large, score badge, tags, résumé IA
- Metadata: upvotes, commentaires, temps de lecture
- Actions: ouvrir lien, favoris, marquer lu, archiver, partager, notes

### Filtres et Recherche

**Filtres progressifs:**
- Search bar pleine largeur (debounce 300ms)
- Chips catégories cliquables (multi-select)
- Chips sources (toggle on/off)
- Dropdown tri (score, date, popularité)
- Compteur résultats + bouton clear all

### Actions Utilisateur

**Actions complètes:**
- Ouvrir lien externe (nouvel onglet)
- Toggle favoris (animation cœur, optimistic update)
- Marquer lu/non lu
- Archiver/désarchiver
- Partager (copie lien, toast confirmation)
- Ajouter notes personnelles (modal)

**Gestures mobile:**
- Swipe droite → Marquer lu
- Swipe gauche → Archiver
- Long press → Menu contextuel
- Pull-to-refresh → Reload articles

### Configuration

**3 onglets (Tabs):**

**1. Mots-clés:**
- Tableau interactif (tri, filtre, recherche)
- Colonnes: Keyword, Catégorie, Poids (1-5), Actif, Actions
- Modal ajout/édition avec React Hook Form + Zod
- Bulk actions (activer/désactiver plusieurs, supprimer)
- Import/export CSV

**2. Sources:**
- Cards par source (Reddit, HackerNews, Dev.to, GitHub, Medium)
- Toggle actif/inactif
- Configuration expandable (accordion):
  - Max articles (slider)
  - Config spécifique (subreddits, tags, etc.)
  - Fréquence scraping
- Bouton "Tester maintenant" (trigger manuel)
- Indicateurs: statut, nb articles 24h, taux succès

**3. Préférences:**
- Email digest (toggle, heure, fréquence, seuil score)
- Affichage (catégories préférées, articles/page, langue)
- Notifications (nouveaux articles >80, tendances)
- Auto-save après 2s

### Analytics

**Power BI Embedded:**
- Composant wrapper `powerbi-client-react`
- API Route Next.js pour générer embed tokens
- Refresh auto token (55 min)
- Header: sélecteur période, refresh, plein écran
- Thème synchronisé (light/dark/techwatch)
- Mobile responsive avec touch gestures
- Error boundary avec retry

### Thèmes

**3 thèmes:**
- **Light**: Fond blanc/gris clair, design épuré
- **Dark**: Fond sombre, contraste élevé
- **TechWatch** (signature): Bleu foncé (220 25% 10%), accent cyan/violet, gradients

**Toggle:**
- Icône sun/moon dans sidebar footer
- Persisté localStorage + Zustand
- Transition smooth via CSS variables

### State Management

**Séparation claire:**

**TanStack Query** (données serveur):
- Articles (infinite query)
- Keywords, Sources (queries simples)
- Optimistic updates (favoris, lu, archiver)
- Cache automatique (2 min stale time)
- Refetch on window focus

**Zustand** (UI state):
- Sidebar collapsed
- Thème actif
- Filtres actifs (search, categories, sources, sort)
- Modals open/close
- Persisté localStorage avec middleware

### Performance

**Optimisations:**
- **Virtualization**: react-virtuoso pour infinite scroll
- **Code splitting**: Dynamic imports pages/composants lourds
- **Image optimization**: Next.js Image avec lazy loading, WebP
- **Memoization**: React.memo sur ArticleCard
- **Debouncing**: Search 300ms, filters 200ms
- **Prefetching**: Next page avant scroll
- **Bundle**: <300KB gzipped initial

**Animations:**
- Framer Motion pour transitions
- Staggered loading cards
- Skeleton screens (pas de spinners)
- Spring physics pour gestures

### Responsive

**Breakpoints:**
- Mobile: <768px
- Tablet: 768px-1024px
- Desktop: >1024px

**Adaptations:**
- **Mobile**: Bottom nav, full-screen pages, swipe gestures, pull-to-refresh
- **Tablet**: Sidebar collapsible, hover expand
- **Desktop**: Sidebar fixe, 2 colonnes cards, hover effects

## Architecture Technique

### Structure Fichiers

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout + providers
│   ├── page.tsx                # Feed page
│   ├── config/
│   │   └── page.tsx            # Configuration page
│   ├── analytics/
│   │   └── page.tsx            # Analytics page
│   ├── api/
│   │   └── powerbi/
│   │       └── token/
│   │           └── route.ts    # Embed token generation
│   └── globals.css             # Thème TechWatch variables
│
├── components/
│   ├── ui/                     # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── switch.tsx
│   │   ├── slider.tsx
│   │   ├── dialog.tsx
│   │   ├── sheet.tsx
│   │   ├── tabs.tsx
│   │   ├── accordion.tsx
│   │   ├── toast.tsx
│   │   └── skeleton.tsx
│   │
│   ├── layout/
│   │   ├── Sidebar.tsx         # Desktop/tablet sidebar
│   │   ├── BottomNav.tsx       # Mobile navigation
│   │   ├── TopBar.tsx          # Mobile top bar
│   │   └── ThemeToggle.tsx     # Theme switcher
│   │
│   ├── feed/
│   │   ├── ArticleCard.tsx     # Card article
│   │   ├── FilterBar.tsx       # Search + filtres
│   │   ├── ArticleFeed.tsx     # Feed virtualisé
│   │   └── ArticleModal.tsx    # Modal détails
│   │
│   ├── config/
│   │   ├── KeywordManager.tsx  # Gestion keywords
│   │   ├── KeywordModal.tsx    # Add/Edit keyword
│   │   ├── SourceCard.tsx      # Card source
│   │   └── PreferencesForm.tsx # Formulaire prefs
│   │
│   ├── analytics/
│   │   └── PowerBIDashboard.tsx # Embed Power BI
│   │
│   └── common/
│       ├── EmptyState.tsx      # États vides
│       ├── ErrorBoundary.tsx   # Error handling
│       └── LoadingSpinner.tsx  # Loaders
│
├── hooks/
│   ├── useArticles.ts          # TanStack Query articles
│   ├── useToggleFavorite.ts    # Mutation favoris
│   ├── useMarkRead.ts          # Mutation lu
│   ├── useArchive.ts           # Mutation archive
│   ├── useKeywords.ts          # Query keywords
│   ├── useSources.ts           # Query sources
│   ├── usePullToRefresh.ts     # Pull to refresh
│   └── useTheme.ts             # Theme management
│
├── store/
│   ├── ui-store.ts             # Zustand UI state
│   └── modals-store.ts         # Zustand modals
│
├── lib/
│   ├── api-client.ts           # Axios client + APIs
│   ├── utils.ts                # cn, formatDate, etc.
│   ├── validators.ts           # Zod schemas
│   └── animations.ts           # Framer Motion variants
│
└── types/
    └── index.ts                # Types TypeScript
```

### Stack Technique

**Core:**
- Next.js 14 (App Router)
- React 18
- TypeScript

**Styling:**
- TailwindCSS
- shadcn/ui (composants)
- Framer Motion (animations)
- class-variance-authority (variants)

**State:**
- TanStack Query (server state)
- Zustand (UI state)

**Forms:**
- React Hook Form
- Zod (validation)

**Utils:**
- axios (HTTP)
- date-fns (dates)
- lucide-react (icons)
- recharts (graphiques si nécessaire)
- powerbi-client-react (Power BI)

**Performance:**
- react-virtuoso (virtualization)
- Next.js Image (optimization images)

**Testing:**
- Vitest
- Testing Library

## Composants Détaillés

### ArticleCard

**Props:**
```typescript
interface ArticleCardProps {
  article: Article;
  onToggleFavorite: (id: string) => void;
  onMarkRead: (id: string) => void;
  onArchive: (id: string) => void;
  onShare: (id: string) => void;
  onAddNote: (id: string, note: string) => void;
  variant?: 'default' | 'compact';
}
```

**Structure:**
```tsx
<Card className="group hover:scale-[1.02] transition-transform">
  {/* Header */}
  <div className="flex items-center gap-2">
    <img src={sourceFavicon} className="w-4 h-4" />
    <span className="text-sm text-muted">{source.name}</span>
    <span className="text-sm text-muted">•</span>
    <span className="text-sm text-muted">{formatRelative(publishedAt)}</span>
  </div>

  {/* Score Badge */}
  <Badge className={getScoreColor(score)}>{score}</Badge>

  {/* Title */}
  <h3 className="text-lg font-bold mt-2 line-clamp-2">{title}</h3>

  {/* Tags */}
  <div className="flex gap-2 mt-2">
    <Badge variant="outline">{category}</Badge>
    {tags.slice(0, 3).map(tag => <Badge variant="secondary">{tag}</Badge>)}
  </div>

  {/* Summary AI */}
  <p className="text-sm text-muted mt-3 line-clamp-3">{summary}</p>

  {/* Metadata */}
  <div className="flex gap-4 mt-3 text-sm text-muted">
    <span><ThumbsUp className="w-4 h-4" /> {upvotes}</span>
    <span><MessageSquare className="w-4 h-4" /> {comments}</span>
    <span><Clock className="w-4 h-4" /> {readTime} min</span>
  </div>

  {/* Actions */}
  <div className="flex gap-2 mt-4">
    <Button variant="ghost" size="sm" onClick={onOpen}>
      <ExternalLink />
    </Button>
    <Button variant="ghost" size="sm" onClick={onToggleFavorite}>
      <Star className={isFavorite ? 'fill-current' : ''} />
    </Button>
    <Button variant="ghost" size="sm" onClick={onMarkRead}>
      <CheckCircle className={isRead ? 'fill-current' : ''} />
    </Button>
    <Button variant="ghost" size="sm" onClick={onArchive}>
      <Archive />
    </Button>
    <Button variant="ghost" size="sm" onClick={onShare}>
      <Share />
    </Button>
    <Button variant="ghost" size="sm" onClick={onAddNote}>
      <MessageSquare />
    </Button>
  </div>
</Card>
```

**Animations:**
- Entrance: `fadeInUp` staggered
- Hover: `scale(1.02)` + shadow increase
- Favorite: Heart bounce with spring
- Mobile swipe: TranslateX avec indicateur couleur

### FilterBar

**Structure:**
```tsx
<div className="space-y-4">
  {/* Search */}
  <Input
    placeholder="Rechercher des articles..."
    value={search}
    onChange={(e) => debouncedSetSearch(e.target.value)}
    icon={<Search />}
  />

  {/* Categories */}
  <div className="flex flex-wrap gap-2">
    {categories.map(cat => (
      <Badge
        variant={activeCategories.includes(cat) ? 'default' : 'outline'}
        className="cursor-pointer"
        onClick={() => toggleCategory(cat)}
      >
        {cat} ({articleCounts[cat]})
      </Badge>
    ))}
  </div>

  {/* Sources */}
  <div className="flex flex-wrap gap-2">
    {sources.map(source => (
      <Badge
        variant={activeSources.includes(source) ? 'default' : 'secondary'}
        className="cursor-pointer"
        onClick={() => toggleSource(source)}
      >
        {source}
      </Badge>
    ))}
  </div>

  {/* Sort + Clear */}
  <div className="flex justify-between items-center">
    <Select value={sort} onValueChange={setSort}>
      <SelectTrigger>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="score">Score (desc)</SelectItem>
        <SelectItem value="date">Plus récent</SelectItem>
        <SelectItem value="popularity">Popularité</SelectItem>
      </SelectContent>
    </Select>

    <Button variant="ghost" onClick={clearFilters}>
      Effacer filtres
    </Button>
  </div>

  {/* Results count */}
  <p className="text-sm text-muted">{count} articles trouvés</p>
</div>
```

### Sidebar

**Desktop/Tablet:**
```tsx
<aside className={cn(
  "fixed left-0 top-0 h-screen bg-card border-r transition-all",
  collapsed ? "w-20" : "w-[280px]"
)}>
  {/* Header */}
  <div className="p-4 border-b flex items-center justify-between">
    {!collapsed && <Logo />}
    <Button variant="ghost" size="icon" onClick={toggleSidebar}>
      {collapsed ? <ChevronRight /> : <ChevronLeft />}
    </Button>
  </div>

  {/* Nav Items */}
  <nav className="p-2 space-y-1">
    <NavItem href="/" icon={<Home />} label="Feed" collapsed={collapsed} />
    <NavItem href="/config" icon={<Settings />} label="Configuration" collapsed={collapsed} />
    <NavItem href="/analytics" icon={<BarChart />} label="Analytics" collapsed={collapsed} />
  </nav>

  {/* Footer */}
  <div className="absolute bottom-0 left-0 right-0 p-4 border-t space-y-2">
    <ThemeToggle collapsed={collapsed} />
    <UserMenu collapsed={collapsed} />
  </div>
</aside>
```

**Mobile Bottom Nav:**
```tsx
<nav className="fixed bottom-0 left-0 right-0 bg-card border-t flex justify-around p-2">
  <NavButton href="/" icon={<Home />} label="Feed" />
  <NavButton href="/config" icon={<Settings />} label="Config" />
  <NavButton href="/analytics" icon={<BarChart />} label="Analytics" />
</nav>
```

### PowerBIDashboard

```tsx
import { PowerBIEmbed } from 'powerbi-client-react';
import { models } from 'powerbi-client';

export const PowerBIDashboard = () => {
  const [embedToken, setEmbedToken] = useState<string>();
  const theme = useUIStore(s => s.theme);

  useEffect(() => {
    // Fetch embed token from API route
    fetch('/api/powerbi/token')
      .then(r => r.json())
      .then(data => setEmbedToken(data.token));
  }, []);

  if (!embedToken) return <DashboardSkeleton />;

  const config: models.IReportEmbedConfiguration = {
    type: 'report',
    tokenType: models.TokenType.Embed,
    accessToken: embedToken,
    embedUrl: process.env.NEXT_PUBLIC_POWERBI_EMBED_URL!,
    id: process.env.NEXT_PUBLIC_POWERBI_REPORT_ID!,
    settings: {
      panes: { filters: { expanded: false, visible: true } },
      background: models.BackgroundType.Transparent,
      navContentPaneEnabled: true
    },
    theme: getPowerBITheme(theme)
  };

  return (
    <div className="h-[calc(100vh-8rem)]">
      <PowerBIEmbed
        embedConfig={config}
        cssClassName="w-full h-full"
      />
    </div>
  );
};
```

## Hooks TanStack Query

### useArticles

```typescript
interface ArticleFilters {
  search?: string;
  categories?: string[];
  sources?: string[];
  sort?: 'score' | 'date' | 'popularity';
  minScore?: number;
}

export const useArticles = (filters: ArticleFilters) => {
  return useInfiniteQuery({
    queryKey: ['articles', filters],
    queryFn: async ({ pageParam = 0 }) => {
      const response = await articlesApi.getArticles({
        ...filters,
        offset: pageParam,
        limit: 50
      });
      return response.data;
    },
    getNextPageParam: (lastPage, allPages) => {
      return lastPage.hasMore ? allPages.length * 50 : undefined;
    },
    initialPageParam: 0,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchOnWindowFocus: true
  });
};
```

### useToggleFavorite (Optimistic)

```typescript
export const useToggleFavorite = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: string) => articlesApi.toggleFavorite(articleId),

    onMutate: async (articleId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['articles'] });

      // Snapshot
      const previousData = queryClient.getQueryData(['articles']);

      // Optimistic update
      queryClient.setQueriesData({ queryKey: ['articles'] }, (old: any) => {
        if (!old) return old;
        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            articles: page.articles.map((article: Article) =>
              article.id === articleId
                ? { ...article, is_favorite: !article.is_favorite }
                : article
            )
          }))
        };
      });

      return { previousData };
    },

    onError: (err, variables, context) => {
      // Rollback
      if (context?.previousData) {
        queryClient.setQueryData(['articles'], context.previousData);
      }
      toast.error("Erreur lors de la mise à jour");
    },

    onSuccess: () => {
      toast.success("Favoris mis à jour");
    }
  });
};
```

## Zustand Stores

### UI Store

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'techwatch';
  activeFilters: {
    search: string;
    categories: string[];
    sources: string[];
    sort: 'score' | 'date' | 'popularity';
  };

  // Actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark' | 'techwatch') => void;
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
        sort: 'score'
      },

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      setSidebarCollapsed: (collapsed) =>
        set({ sidebarCollapsed: collapsed }),

      setTheme: (theme) => {
        set({ theme });
        // Update CSS
        document.documentElement.setAttribute('data-theme', theme);
      },

      setFilters: (filters) =>
        set((state) => ({
          activeFilters: { ...state.activeFilters, ...filters }
        })),

      clearFilters: () =>
        set({
          activeFilters: {
            search: '',
            categories: [],
            sources: [],
            sort: 'score'
          }
        })
    }),
    {
      name: 'techwatch-ui-store',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme
      })
    }
  )
);
```

### Modals Store

```typescript
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
    set({ noteModal: { open: false, articleId: null } })
}));
```

## Animations Framer Motion

### Variants

```typescript
// lib/animations.ts
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] }
};

export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1
    }
  }
};

export const scaleIn = {
  initial: { scale: 0.95, opacity: 0 },
  animate: { scale: 1, opacity: 1 },
  exit: { scale: 0.95, opacity: 0 },
  transition: { duration: 0.2 }
};

export const slideInFromRight = {
  initial: { x: '100%' },
  animate: { x: 0 },
  exit: { x: '100%' },
  transition: { type: 'spring', damping: 30, stiffness: 300 }
};
```

### Usage

```tsx
// Page transitions
<motion.div
  initial="initial"
  animate="animate"
  exit="exit"
  variants={fadeInUp}
>
  {children}
</motion.div>

// Staggered cards
<motion.div variants={staggerContainer} initial="initial" animate="animate">
  {articles.map(article => (
    <motion.div key={article.id} variants={fadeInUp}>
      <ArticleCard article={article} />
    </motion.div>
  ))}
</motion.div>

// Modal
<Dialog open={open} onOpenChange={setOpen}>
  <motion.div variants={scaleIn} initial="initial" animate="animate" exit="exit">
    <DialogContent>{children}</DialogContent>
  </motion.div>
</Dialog>
```

## Thème TechWatch Personnalisé

### CSS Variables

```css
/* app/globals.css */

[data-theme="techwatch"] {
  --background: 220 25% 10%;           /* Bleu très foncé #141B2B */
  --foreground: 210 40% 98%;           /* Blanc cassé #F9FAFB */

  --card: 220 20% 15%;                 /* Cards #1E2433 */
  --card-foreground: 210 40% 98%;

  --popover: 220 20% 15%;
  --popover-foreground: 210 40% 98%;

  --primary: 200 100% 50%;             /* Cyan vif #00BFFF */
  --primary-foreground: 220 25% 10%;

  --secondary: 220 15% 25%;            /* Gris-bleu */
  --secondary-foreground: 210 40% 98%;

  --muted: 220 15% 20%;
  --muted-foreground: 215 20% 65%;

  --accent: 270 80% 60%;               /* Violet #A855F7 */
  --accent-foreground: 210 40% 98%;

  --destructive: 0 84% 60%;            /* Rouge */
  --destructive-foreground: 210 40% 98%;

  --border: 220 20% 20%;
  --input: 220 20% 18%;
  --ring: 200 100% 50%;

  --radius: 0.5rem;
}

/* Gradients signature */
.gradient-primary {
  background: linear-gradient(135deg, var(--primary), var(--accent));
}

.gradient-score-low {
  background: linear-gradient(135deg, #EF4444, #F59E0B);
}

.gradient-score-medium {
  background: linear-gradient(135deg, #F59E0B, #10B981);
}

.gradient-score-high {
  background: linear-gradient(135deg, #10B981, #06B6D4);
}
```

## Gestures Mobiles

### Pull-to-Refresh

```typescript
// hooks/usePullToRefresh.ts
export const usePullToRefresh = (onRefresh: () => Promise<void>) => {
  const [isPulling, setIsPulling] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const startY = useRef(0);

  useEffect(() => {
    const handleTouchStart = (e: TouchEvent) => {
      if (window.scrollY === 0) {
        startY.current = e.touches[0].clientY;
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (window.scrollY === 0 && startY.current) {
        const distance = e.touches[0].clientY - startY.current;
        if (distance > 0) {
          setPullDistance(Math.min(distance, 100));
          setIsPulling(distance > 60);
        }
      }
    };

    const handleTouchEnd = async () => {
      if (isPulling) {
        await onRefresh();
      }
      setPullDistance(0);
      setIsPulling(false);
      startY.current = 0;
    };

    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchmove', handleTouchMove);
    document.addEventListener('touchend', handleTouchEnd);

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, [isPulling, onRefresh]);

  return { isPulling, pullDistance };
};
```

### Swipe Cards

```tsx
// components/feed/SwipeableCard.tsx
import { motion, useMotionValue, useTransform } from 'framer-motion';

export const SwipeableCard = ({ article, onMarkRead, onArchive, children }) => {
  const x = useMotionValue(0);
  const background = useTransform(
    x,
    [-150, 0, 150],
    ['#EF4444', '#FFFFFF', '#10B981']
  );

  const handleDragEnd = (event, info) => {
    if (info.offset.x > 100) {
      onMarkRead(article.id);
    } else if (info.offset.x < -100) {
      onArchive(article.id);
    }
  };

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.2}
      style={{ x, background }}
      onDragEnd={handleDragEnd}
      className="relative"
    >
      {/* Indicators */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white">
        <CheckCircle className="w-8 h-8" />
      </div>
      <div className="absolute right-4 top-1/2 -translate-y-1/2 text-white">
        <Archive className="w-8 h-8" />
      </div>

      {children}
    </motion.div>
  );
};
```

## Performance Optimizations

### Virtualization

```tsx
// components/feed/ArticleFeed.tsx
import { Virtuoso } from 'react-virtuoso';

export const ArticleFeed = () => {
  const { data, fetchNextPage, hasNextPage, isLoading } = useArticles(filters);

  const articles = data?.pages.flatMap(page => page.articles) ?? [];

  return (
    <Virtuoso
      data={articles}
      endReached={() => hasNextPage && fetchNextPage()}
      itemContent={(index, article) => (
        <ArticleCard key={article.id} article={article} />
      )}
      components={{
        Footer: () => hasNextPage ? <LoadingSpinner /> : null,
        EmptyPlaceholder: () => <EmptyState type="no-articles" />
      }}
      style={{ height: 'calc(100vh - 12rem)' }}
    />
  );
};
```

### Code Splitting

```tsx
// Dynamic imports
const PowerBIDashboard = dynamic(
  () => import('@/components/analytics/PowerBIDashboard'),
  {
    loading: () => <DashboardSkeleton />,
    ssr: false // Power BI client-side only
  }
);

const ArticleModal = dynamic(
  () => import('@/components/feed/ArticleModal')
);

const KeywordModal = dynamic(
  () => import('@/components/config/KeywordModal')
);
```

### Image Optimization

```tsx
import Image from 'next/image';

<Image
  src={article.imageUrl || '/placeholder.png'}
  alt={article.title}
  width={400}
  height={200}
  className="rounded-t-lg"
  loading="lazy"
  placeholder="blur"
  blurDataURL="/placeholder-blur.png"
/>
```

### Memoization

```tsx
const MemoizedArticleCard = memo(
  ArticleCard,
  (prev, next) =>
    prev.article.id === next.article.id &&
    prev.article.is_favorite === next.article.is_favorite &&
    prev.article.is_read === next.article.is_read &&
    prev.article.is_archived === next.article.is_archived
);
```

## Testing Strategy

### Unit Tests (Vitest)

```typescript
// components/__tests__/ArticleCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ArticleCard } from '../ArticleCard';

describe('ArticleCard', () => {
  const mockArticle = {
    id: '1',
    title: 'Test Article',
    url: 'https://example.com',
    score: 85,
    category: 'dev',
    is_favorite: false,
    is_read: false
  };

  it('renders article title', () => {
    render(<ArticleCard article={mockArticle} />);
    expect(screen.getByText('Test Article')).toBeInTheDocument();
  });

  it('toggles favorite on click', () => {
    const onToggleFavorite = vi.fn();
    render(<ArticleCard article={mockArticle} onToggleFavorite={onToggleFavorite} />);

    const favoriteButton = screen.getByRole('button', { name: /favorite/i });
    fireEvent.click(favoriteButton);

    expect(onToggleFavorite).toHaveBeenCalledWith('1');
  });
});
```

### Integration Tests

```typescript
// hooks/__tests__/useArticles.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useArticles } from '../useArticles';

const createWrapper = () => {
  const queryClient = new QueryClient();
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useArticles', () => {
  it('fetches articles successfully', async () => {
    const { result } = renderHook(() => useArticles({}), {
      wrapper: createWrapper()
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.pages[0].articles).toBeDefined();
  });
});
```

## Métriques de Succès

### Performance
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Largest Contentful Paint: <2.5s
- Cumulative Layout Shift: <0.1
- Bundle initial: <300KB gzipped

### UX
- Animations 60fps
- Infinite scroll fluide
- Optimistic updates <50ms perceived
- Mobile gestures réactifs

### Qualité Code
- Coverage tests: >80%
- TypeScript strict mode
- ESLint zero errors
- Lighthouse score: >90

## Prochaines Étapes

1. Setup Next.js 14 + TailwindCSS + shadcn/ui
2. Configurer TanStack Query + Zustand
3. Implémenter layout (Sidebar, TopBar, BottomNav)
4. Développer composants UI de base
5. Implémenter page Feed (ArticleCard, FilterBar, virtualization)
6. Implémenter page Configuration (Keywords, Sources, Preferences)
7. Intégrer Power BI Dashboard
8. Implémenter thèmes (Light, Dark, TechWatch)
9. Ajouter animations Framer Motion
10. Optimiser performance (code splitting, memoization)
11. Implémenter gestures mobiles
12. Tests unitaires et d'intégration
13. Documentation composants

---

**Dernière mise à jour**: Décembre 2024
**Version**: 1.0.0
**Auteur**: Tom (Epitech Lyon)
