# Frontend 3D Theme Redesign - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform ZenWatch frontend with premium violet/magenta 3D theme - immersive home page, minimal articles page

**Architecture:** Two-tier UI experience - 3D animated home with parallax and card transforms, clean minimal articles/config pages with subtle transitions only

**Tech Stack:** Next.js 14, TypeScript, Framer Motion, Tailwind CSS, CSS 3D transforms

---

## Task 1: Install Dependencies

**Files:**
- Modify: `package.json`

**Step 1: Install react-intersection-observer**

Run:
```bash
npm install react-intersection-observer
```

Expected: Package installed successfully

**Step 2: Verify installation**

Run:
```bash
npm list react-intersection-observer framer-motion
```

Expected: Both packages listed

**Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "chore: add react-intersection-observer dependency"
```

---

## Task 2: Update Tailwind Color Palette

**Files:**
- Modify: `tailwind.config.ts`

**Step 1: Update colors section with violet/magenta palette**

Replace the `colors` section in `extend` with:

```typescript
colors: {
  border: 'hsl(var(--border))',
  input: 'hsl(var(--input))',
  ring: 'hsl(var(--ring))',
  background: 'hsl(var(--background))',
  foreground: 'hsl(var(--foreground))',
  primary: {
    DEFAULT: 'hsl(var(--primary))',
    foreground: 'hsl(var(--primary-foreground))'
  },
  secondary: {
    DEFAULT: 'hsl(var(--secondary))',
    foreground: 'hsl(var(--secondary-foreground))'
  },
  destructive: {
    DEFAULT: 'hsl(var(--destructive))',
    foreground: 'hsl(var(--destructive-foreground))'
  },
  muted: {
    DEFAULT: 'hsl(var(--muted))',
    foreground: 'hsl(var(--muted-foreground))'
  },
  accent: {
    DEFAULT: 'hsl(var(--accent))',
    foreground: 'hsl(var(--accent-foreground))'
  },
  popover: {
    DEFAULT: 'hsl(var(--popover))',
    foreground: 'hsl(var(--popover-foreground))'
  },
  card: {
    DEFAULT: 'hsl(var(--card))',
    foreground: 'hsl(var(--card-foreground))'
  },
  chart: {
    '1': 'hsl(var(--chart-1))',
    '2': 'hsl(var(--chart-2))',
    '3': 'hsl(var(--chart-3))',
    '4': 'hsl(var(--chart-4))',
    '5': 'hsl(var(--chart-5))'
  },
  violet: {
    DEFAULT: '#8B5CF6',
    light: '#A78BFA',
    dark: '#7C3AED',
    50: '#F5F3FF',
    100: '#EDE9FE',
    200: '#DDD6FE',
    300: '#C4B5FD',
    400: '#A78BFA',
    500: '#8B5CF6',
    600: '#7C3AED',
    700: '#6D28D9',
    800: '#5B21B6',
    900: '#4C1D95',
  },
  magenta: {
    DEFAULT: '#D946EF',
    light: '#E879F9',
    dark: '#C026D3',
    50: '#FDF4FF',
    100: '#FAE8FF',
    200: '#F5D0FE',
    300: '#F0ABFC',
    400: '#E879F9',
    500: '#D946EF',
    600: '#C026D3',
    700: '#A21CAF',
    800: '#86198F',
    900: '#701A75',
  },
  anthracite: {
    950: '#0D0D0D',
    900: '#1A1A1D',
    800: '#25252A',
    700: '#2D2D32',
    600: '#3A3A40',
  }
},
```

**Step 2: Verify Tailwind config compiles**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 3: Commit**

```bash
git add tailwind.config.ts
git commit -m "feat(theme): update Tailwind palette to violet/magenta/anthracite"
```

---

## Task 3: Update Global CSS Variables

**Files:**
- Modify: `app/globals.css`

**Step 1: Update dark theme CSS variables**

Replace the `.dark` section in `@layer base` with:

```css
.dark {
  --background: 210 11% 6%;           /* #0D0D0D */
  --foreground: 0 0% 96%;             /* #F5F5F7 */
  --card: 210 11% 10%;                /* #1A1A1D */
  --card-foreground: 0 0% 96%;        /* #F5F5F7 */
  --popover: 210 11% 10%;             /* #1A1A1D */
  --popover-foreground: 0 0% 96%;     /* #F5F5F7 */
  --primary: 266 91% 65%;             /* #8B5CF6 violet */
  --primary-foreground: 0 0% 6%;      /* #0D0D0D */
  --secondary: 210 11% 15%;           /* #25252A */
  --secondary-foreground: 0 0% 96%;   /* #F5F5F7 */
  --muted: 210 11% 15%;               /* #25252A */
  --muted-foreground: 0 0% 63%;       /* #A1A1AA */
  --accent: 291 76% 60%;              /* #D946EF magenta */
  --accent-foreground: 0 0% 6%;       /* #0D0D0D */
  --destructive: 0 84% 60%;
  --destructive-foreground: 0 0% 96%;
  --border: 210 11% 18%;              /* #2D2D32 */
  --input: 210 11% 15%;               /* #25252A */
  --ring: 266 91% 65%;                /* #8B5CF6 violet */
  --chart-1: 266 91% 65%;
  --chart-2: 291 76% 60%;
  --chart-3: 262 83% 58%;
  --chart-4: 270 95% 75%;
  --chart-5: 280 89% 65%;
}
```

**Step 2: Add gradient utility classes**

Add before the existing utilities:

```css
@layer utilities {
  /* Gradient backgrounds */
  .bg-gradient-violet-magenta {
    background: linear-gradient(135deg, #8B5CF6 0%, #D946EF 100%);
  }

  .bg-gradient-subtle {
    background: linear-gradient(180deg, rgba(139, 92, 246, 0.1) 0%, rgba(217, 70, 239, 0.05) 100%);
  }

  .bg-gradient-glow {
    background: radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.3), transparent 70%);
  }

  /* Text gradients */
  .text-gradient-violet {
    background: linear-gradient(135deg, #8B5CF6 0%, #D946EF 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  /* 3D transform utilities */
  .transform-3d {
    transform-style: preserve-3d;
    perspective: 1000px;
  }

  .card-3d-hover {
    transition: transform 0.6s cubic-bezier(0.23, 1, 0.32, 1);
  }

  .card-3d-hover:hover {
    transform: perspective(1000px) rotateX(-5deg) rotateY(5deg) translateZ(20px);
  }
}
```

**Step 3: Update scrollbar colors**

Replace the scrollbar section with:

```css
@layer base {
  /* Firefox scrollbar support */
  * {
    scrollbar-width: thin;
    scrollbar-color: #8B5CF6 #0D0D0D;
  }

  /* Webkit scrollbar (Chrome, Safari, Edge) */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: #0D0D0D;
  }

  ::-webkit-scrollbar-thumb {
    background: #7C3AED;
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #8B5CF6;
  }

  ::selection {
    background: #8B5CF6;
    color: #0D0D0D;
  }
}
```

**Step 4: Test build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 5: Commit**

```bash
git add app/globals.css
git commit -m "feat(theme): update CSS variables and add gradient utilities"
```

---

## Task 4: Create 3D Animation Library

**Files:**
- Create: `lib/animations-3d.ts`

**Step 1: Create animations-3d.ts file**

```typescript
import { Variants } from 'framer-motion';

/**
 * 3D card lift animation with rotation
 * Use on cards for premium hover effect
 */
export const card3DLift: Variants = {
  initial: {
    rotateX: 0,
    rotateY: 0,
    z: 0,
    scale: 1,
  },
  hover: {
    rotateX: -5,
    rotateY: 5,
    z: 20,
    scale: 1.02,
    transition: {
      duration: 0.6,
      ease: [0.23, 1, 0.32, 1], // Custom easing
    },
  },
};

/**
 * Fade in from bottom with slight rotation
 * Use for scroll-based reveal animations
 */
export const fadeInFromBottom: Variants = {
  hidden: {
    opacity: 0,
    y: 60,
    rotateX: 10,
  },
  visible: {
    opacity: 1,
    y: 0,
    rotateX: 0,
    transition: {
      duration: 0.8,
      ease: [0.23, 1, 0.32, 1],
    },
  },
};

/**
 * Stagger children animations
 * Use on parent containers
 */
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
    },
  },
};

/**
 * Minimal fade in (for articles page)
 * Quick, subtle, performance-friendly
 */
export const minimalFadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};

/**
 * Glow intensity animation
 * Use with box-shadow for hover states
 */
export const glowPulse: Variants = {
  initial: {
    boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)',
  },
  hover: {
    boxShadow: [
      '0 0 20px rgba(139, 92, 246, 0.3)',
      '0 0 40px rgba(217, 70, 239, 0.5)',
      '0 0 20px rgba(139, 92, 246, 0.3)',
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};
```

**Step 2: Verify TypeScript compilation**

Run:
```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add lib/animations-3d.ts
git commit -m "feat(lib): add 3D animation variants library"
```

---

## Task 5: Create Parallax Scroll Hook

**Files:**
- Create: `lib/scroll-parallax.ts`

**Step 1: Create scroll-parallax.ts file**

```typescript
import { useEffect, useState, useCallback, RefObject } from 'react';

interface ParallaxOptions {
  speed?: number; // Scroll speed multiplier (0-1, lower = slower)
  direction?: 'vertical' | 'horizontal';
}

/**
 * Custom hook for parallax scroll effect
 * @param speed - Scroll speed multiplier (default: 0.5)
 * @param direction - Scroll direction (default: 'vertical')
 * @returns Transform CSS value for parallax effect
 */
export const useParallax = (
  options: ParallaxOptions = {}
): { ref: RefObject<HTMLDivElement> | null; transform: string } => {
  const { speed = 0.5, direction = 'vertical' } = options;
  const [offset, setOffset] = useState(0);

  const handleScroll = useCallback(() => {
    const scrolled = window.pageYOffset;
    setOffset(scrolled * (1 - speed));
  }, [speed]);

  useEffect(() => {
    // Throttle scroll events for performance
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, [handleScroll]);

  const transform =
    direction === 'vertical'
      ? `translateY(${offset}px)`
      : `translateX(${offset}px)`;

  return { ref: null, transform };
};

/**
 * Check if user prefers reduced motion
 * Disable parallax and 3D effects if true
 */
export const usePrefersReducedMotion = (): boolean => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
};
```

**Step 2: Verify TypeScript compilation**

Run:
```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add lib/scroll-parallax.ts
git commit -m "feat(lib): add parallax scroll and reduced motion hooks"
```

---

## Task 6: Create ParallaxGrid Component

**Files:**
- Create: `components/home/ParallaxGrid.tsx`

**Step 1: Create ParallaxGrid component**

```typescript
'use client';

import { useParallax, usePrefersReducedMotion } from '@/lib/scroll-parallax';

export const ParallaxGrid = () => {
  const { transform } = useParallax({ speed: 0.7 });
  const prefersReducedMotion = usePrefersReducedMotion();

  if (prefersReducedMotion) {
    return null; // Don't render parallax if user prefers reduced motion
  }

  return (
    <div
      className="fixed inset-0 pointer-events-none overflow-hidden"
      style={{ zIndex: 0 }}
    >
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-anthracite-950 via-anthracite-900 to-anthracite-950" />

      {/* Animated grid layer */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          transform: prefersReducedMotion ? 'none' : transform,
          backgroundImage: `
            linear-gradient(to right, rgba(139, 92, 246, 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(139, 92, 246, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '80px 80px',
          animation: prefersReducedMotion ? 'none' : 'gridPulse 3s ease-in-out infinite',
        }}
      />

      {/* Glow orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-glow blur-3xl opacity-20 animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gradient-glow blur-3xl opacity-20 animate-pulse" />
    </div>
  );
};
```

**Step 2: Add grid pulse animation to globals.css**

Add to the `@layer utilities` section:

```css
@keyframes gridPulse {
  0%, 100% {
    opacity: 0.1;
  }
  50% {
    opacity: 0.2;
  }
}

.animate-gridPulse {
  animation: gridPulse 3s ease-in-out infinite;
}
```

**Step 3: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 4: Commit**

```bash
git add components/home/ParallaxGrid.tsx app/globals.css
git commit -m "feat(home): add ParallaxGrid component with animated background"
```

---

## Task 7: Create Hero3D Component

**Files:**
- Create: `components/home/Hero3D.tsx`

**Step 1: Create Hero3D component**

```typescript
'use client';

import { motion } from 'framer-motion';
import { fadeInFromBottom } from '@/lib/animations-3d';

export const Hero3D = () => {
  return (
    <motion.section
      className="relative z-10 min-h-[40vh] flex flex-col items-center justify-center px-4 py-16"
      initial="hidden"
      animate="visible"
      variants={fadeInFromBottom}
    >
      <motion.h1
        className="text-6xl md:text-8xl font-bold text-center mb-4 text-gradient-violet"
        style={{
          textShadow: '0 0 40px rgba(139, 92, 246, 0.5), 0 0 80px rgba(217, 70, 239, 0.3)',
        }}
      >
        ZENWATCH
      </motion.h1>

      <motion.p
        className="text-xl md:text-2xl text-muted-foreground text-center max-w-2xl"
        variants={fadeInFromBottom}
      >
        Votre veille tech intelligente
      </motion.p>

      <motion.div
        className="mt-8 flex gap-4"
        variants={fadeInFromBottom}
      >
        <a
          href="/articles"
          className="px-6 py-3 bg-gradient-violet-magenta rounded-lg font-semibold hover:opacity-90 transition-opacity"
        >
          Explorer les articles
        </a>
        <a
          href="/config"
          className="px-6 py-3 border border-violet/30 rounded-lg font-semibold hover:bg-violet/10 transition-colors"
        >
          Configurer
        </a>
      </motion.div>
    </motion.section>
  );
};
```

**Step 2: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 3: Commit**

```bash
git add components/home/Hero3D.tsx
git commit -m "feat(home): add Hero3D component with gradient title"
```

---

## Task 8: Create BestArticleCard3D Component

**Files:**
- Create: `components/home/BestArticleCard3D.tsx`

**Step 1: Create BestArticleCard3D component**

```typescript
'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { ExternalLink, TrendingUp } from 'lucide-react';
import { card3DLift, fadeInFromBottom } from '@/lib/animations-3d';
import { usePrefersReducedMotion } from '@/lib/scroll-parallax';
import type { Article } from '@/types';

interface BestArticleCard3DProps {
  article: Article | null;
}

export const BestArticleCard3D = ({ article }: BestArticleCard3DProps) => {
  const { ref, inView } = useInView({ threshold: 0.3, triggerOnce: true });
  const prefersReducedMotion = usePrefersReducedMotion();

  if (!article) {
    return (
      <div className="w-full h-96 rounded-2xl bg-anthracite-800/50 border border-violet/20 flex items-center justify-center">
        <p className="text-muted-foreground">Aucun article cette semaine</p>
      </div>
    );
  }

  return (
    <motion.div
      ref={ref}
      className="w-full h-96 perspective-1000"
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={fadeInFromBottom}
    >
      <motion.div
        className="relative h-full rounded-2xl bg-gradient-to-br from-anthracite-800 to-anthracite-900 border border-violet/30 p-8 overflow-hidden group"
        variants={prefersReducedMotion ? {} : card3DLift}
        initial="initial"
        whileHover="hover"
        style={{
          transformStyle: 'preserve-3d',
          willChange: 'transform',
        }}
      >
        {/* Glow effect */}
        <div className="absolute inset-0 bg-gradient-glow opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        {/* Content */}
        <div className="relative z-10 h-full flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-3 py-1 bg-violet/20 border border-violet/30 rounded-full text-xs font-semibold text-violet-light">
              Article de la semaine
            </span>
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <TrendingUp className="w-4 h-4" />
              <span>{article.score.toFixed(0)}</span>
            </div>
          </div>

          <h3 className="text-2xl font-bold mb-4 line-clamp-3 group-hover:text-gradient-violet transition-all">
            {article.title}
          </h3>

          {article.summary && (
            <p className="text-muted-foreground leading-relaxed line-clamp-4 mb-6">
              {article.summary}
            </p>
          )}

          <div className="mt-auto flex items-center justify-between">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted-foreground capitalize">
                {article.source_type}
              </span>
              {article.author && (
                <span className="text-sm font-medium">{article.author}</span>
              )}
            </div>

            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-full bg-violet/20 hover:bg-violet/30 transition-colors"
            >
              <ExternalLink className="w-5 h-5 text-violet-light" />
            </a>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
```

**Step 2: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 3: Commit**

```bash
git add components/home/BestArticleCard3D.tsx
git commit -m "feat(home): add BestArticleCard3D with 3D hover effect"
```

---

## Task 9: Create BestVideoCard3D Component

**Files:**
- Create: `components/home/BestVideoCard3D.tsx`

**Step 1: Create BestVideoCard3D component**

```typescript
'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Play, ExternalLink } from 'lucide-react';
import { card3DLift, fadeInFromBottom } from '@/lib/animations-3d';
import { usePrefersReducedMotion } from '@/lib/scroll-parallax';
import type { Article } from '@/types';

interface BestVideoCard3DProps {
  video: Article | null;
}

export const BestVideoCard3D = ({ video }: BestVideoCard3DProps) => {
  const { ref, inView } = useInView({ threshold: 0.3, triggerOnce: true });
  const prefersReducedMotion = usePrefersReducedMotion();

  if (!video) {
    return (
      <div className="w-full h-96 rounded-2xl bg-anthracite-800/50 border border-magenta/20 flex items-center justify-center">
        <p className="text-muted-foreground">Aucune vidéo cette semaine</p>
      </div>
    );
  }

  return (
    <motion.div
      ref={ref}
      className="w-full h-96 perspective-1000"
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={fadeInFromBottom}
    >
      <motion.div
        className="relative h-full rounded-2xl bg-gradient-to-br from-anthracite-800 to-anthracite-900 border border-magenta/30 p-8 overflow-hidden group"
        variants={prefersReducedMotion ? {} : card3DLift}
        initial="initial"
        whileHover="hover"
        style={{
          transformStyle: 'preserve-3d',
          willChange: 'transform',
        }}
      >
        {/* Glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-magenta/20 to-violet/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        {/* Content */}
        <div className="relative z-10 h-full flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-3 py-1 bg-magenta/20 border border-magenta/30 rounded-full text-xs font-semibold text-magenta-light">
              Vidéo de la semaine
            </span>
            <Play className="w-4 h-4 text-magenta-light" />
          </div>

          <h3 className="text-2xl font-bold mb-4 line-clamp-3 group-hover:text-gradient-violet transition-all">
            {video.title}
          </h3>

          {video.summary && (
            <p className="text-muted-foreground leading-relaxed line-clamp-4 mb-6">
              {video.summary}
            </p>
          )}

          <div className="mt-auto flex items-center justify-between">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted-foreground capitalize">
                {video.source_type || 'YouTube'}
              </span>
              {video.author && (
                <span className="text-sm font-medium">{video.author}</span>
              )}
            </div>

            <a
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-full bg-magenta/20 hover:bg-magenta/30 transition-colors"
            >
              <ExternalLink className="w-5 h-5 text-magenta-light" />
            </a>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
```

**Step 2: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 3: Commit**

```bash
git add components/home/BestVideoCard3D.tsx
git commit -m "feat(home): add BestVideoCard3D with 3D hover effect"
```

---

## Task 10: Create StatsPreview3D Component

**Files:**
- Create: `components/home/StatsPreview3D.tsx`

**Step 1: Create StatsPreview3D component**

```typescript
'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { BarChart3, TrendingUp, Zap } from 'lucide-react';
import { fadeInFromBottom, staggerContainer } from '@/lib/animations-3d';

export const StatsPreview3D = () => {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });

  const stats = [
    { icon: BarChart3, label: 'Articles analysés', value: '2.5K+', color: 'violet' },
    { icon: TrendingUp, label: 'Score moyen', value: '87', color: 'magenta' },
    { icon: Zap, label: 'Tendances détectées', value: '24', color: 'violet' },
  ];

  return (
    <motion.section
      ref={ref}
      className="relative z-10 w-full max-w-6xl mx-auto px-4 py-16"
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={staggerContainer}
    >
      <motion.h2
        className="text-3xl font-bold text-center mb-12"
        variants={fadeInFromBottom}
      >
        Statistiques en temps réel
      </motion.h2>

      {/* Stats grid */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
        variants={staggerContainer}
      >
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={index}
              className="p-6 rounded-xl bg-anthracite-800/50 border border-violet/20 backdrop-blur-sm"
              variants={fadeInFromBottom}
            >
              <Icon className={`w-8 h-8 text-${stat.color} mb-4`} />
              <div className="text-4xl font-bold text-gradient-violet mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Power BI Placeholder */}
      <motion.div
        className="w-full h-96 rounded-2xl bg-gradient-to-br from-anthracite-800 to-anthracite-900 border border-violet/20 flex items-center justify-center relative overflow-hidden"
        variants={fadeInFromBottom}
      >
        <div className="absolute inset-0 bg-gradient-subtle" />
        <div className="relative z-10 text-center">
          <BarChart3 className="w-16 h-16 text-violet mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Dashboard Power BI</h3>
          <p className="text-muted-foreground">
            Visualisations interactives à venir
          </p>
        </div>
      </motion.div>
    </motion.section>
  );
};
```

**Step 2: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 3: Commit**

```bash
git add components/home/StatsPreview3D.tsx
git commit -m "feat(home): add StatsPreview3D with Power BI placeholder"
```

---

## Task 11: Rewrite Home Page

**Files:**
- Modify: `app/page.tsx`

**Step 1: Replace app/page.tsx content**

```typescript
'use client';

import { ParallaxGrid } from '@/components/home/ParallaxGrid';
import { Hero3D } from '@/components/home/Hero3D';
import { BestArticleCard3D } from '@/components/home/BestArticleCard3D';
import { BestVideoCard3D } from '@/components/home/BestVideoCard3D';
import { StatsPreview3D } from '@/components/home/StatsPreview3D';
import { useArticles } from '@/hooks/use-articles';
import { useMemo } from 'react';

export default function HomePage() {
  // Fetch all articles
  const { data: articlesResponse, isLoading } = useArticles({
    sort: 'score',
    limit: 200,
  });

  const articles = articlesResponse?.data || [];

  // Find best article of the week (highest score, not video)
  const bestArticle = useMemo(() => {
    return articles
      .filter(a => a.source_type !== 'youtube')
      .sort((a, b) => b.score - a.score)[0] || null;
  }, [articles]);

  // Find best video of the week (highest score, YouTube only)
  const bestVideo = useMemo(() => {
    return articles
      .filter(a => a.source_type === 'youtube')
      .sort((a, b) => b.score - a.score)[0] || null;
  }, [articles]);

  return (
    <main className="relative min-h-screen bg-anthracite-950">
      {/* Parallax background */}
      <ParallaxGrid />

      {/* Content */}
      <div className="relative z-10">
        {/* Hero section */}
        <Hero3D />

        {/* Best content cards */}
        <section className="max-w-7xl mx-auto px-4 py-16">
          {isLoading ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="h-96 rounded-2xl bg-anthracite-800/50 animate-pulse" />
              <div className="h-96 rounded-2xl bg-anthracite-800/50 animate-pulse" />
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <BestArticleCard3D article={bestArticle} />
              <BestVideoCard3D video={bestVideo} />
            </div>
          )}
        </section>

        {/* Stats section */}
        <StatsPreview3D />
      </div>
    </main>
  );
}
```

**Step 2: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 3: Commit**

```bash
git add app/page.tsx
git commit -m "feat(home): rewrite home page with 3D components and parallax"
```

---

## Task 12: Update ArticleCard for Minimal Theme

**Files:**
- Modify: `components/feed/ArticleCard.tsx`

**Step 1: Simplify ArticleCard styling**

Replace the return statement with:

```typescript
return (
  <motion.div
    variants={minimalFadeIn}
    initial="hidden"
    animate="visible"
  >
    <div
      className={cn(
        'p-4 bg-anthracite-800/50 border border-violet/20 rounded-lg backdrop-blur-sm',
        'hover:bg-anthracite-800/70 hover:border-violet/40 transition-all duration-150',
        localArticle.is_read && 'opacity-60'
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex-1 min-w-0">
          <h3
            className="font-semibold leading-tight mb-1 cursor-pointer hover:text-violet-light line-clamp-2 transition-colors"
            onClick={() => onOpenModal?.(localArticle.id)}
          >
            {localArticle.title}
          </h3>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="capitalize">{localArticle.source_type}</span>
            <span>•</span>
            <span>{formatRelativeDate(localArticle.published_at)}</span>
            {localArticle.read_time_minutes && (
              <>
                <span>•</span>
                <span>{localArticle.read_time_minutes} min</span>
              </>
            )}
          </div>
        </div>

        {/* Score */}
        <div className="flex flex-col items-center shrink-0">
          <div className={cn(
            'text-2xl font-bold',
            localArticle.score >= 70 ? 'text-violet' : 'text-muted-foreground'
          )}>
            {localArticle.score.toFixed(0)}
          </div>
          <div className="text-xs text-muted-foreground">score</div>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        <span className="px-2 py-0.5 bg-violet/10 border border-violet/20 rounded text-xs">
          {localArticle.category}
        </span>
        {(localArticle.tags || [])
          .filter(tag => tag && tag.trim())
          .slice(0, 3)
          .map((tag) => (
            <span key={tag} className="px-2 py-0.5 bg-anthracite-700/50 border border-violet/10 rounded text-xs">
              {tag}
            </span>
          ))}
      </div>

      {/* Summary */}
      {localArticle.summary && (
        <p
          className={cn(
            'text-sm text-muted-foreground leading-relaxed mb-3',
            !isExpanded && 'line-clamp-2'
          )}
        >
          {localArticle.summary}
        </p>
      )}

      {/* Stats */}
      <div className="flex items-center gap-4 mb-3 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <TrendingUp className="w-3 h-3" />
          {localArticle.upvotes || 0}
        </div>
        <div className="flex items-center gap-1">
          <MessageSquare className="w-3 h-3" />
          {localArticle.comments_count || 0}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between border-t border-violet/10 pt-3">
        <div className="flex items-center gap-2">
          <LikeDislikeButtons
            initialLikes={localArticle.likes}
            initialDislikes={localArticle.dislikes}
            userReaction={localArticle.user_reaction}
            onLike={handleLike}
            onDislike={handleDislike}
            size="sm"
          />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleFavorite.mutate(localArticle.id)}
          >
            <Star
              className={cn(
                'w-4 h-4',
                localArticle.is_favorite && 'fill-violet text-violet'
              )}
            />
          </Button>
          <Button variant="ghost" size="sm">
            <BookmarkPlus className="w-4 h-4" />
          </Button>
        </div>

        <div className="flex items-center gap-1">
          {localArticle.summary && (
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
              href={localArticle.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          </Button>
        </div>
      </div>
    </div>
  </motion.div>
);
```

**Step 2: Import minimalFadeIn**

Add to imports:

```typescript
import { minimalFadeIn } from '@/lib/animations-3d';
```

**Step 3: Remove CornerBrackets import and usage**

Remove:
```typescript
import { CornerBrackets } from '@/components/cyberpunk';
```

**Step 4: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 5: Commit**

```bash
git add components/feed/ArticleCard.tsx
git commit -m "feat(articles): update ArticleCard with minimal violet theme"
```

---

## Task 13: Update FilterBar Styling

**Files:**
- Modify: `components/feed/FilterBar.tsx`

**Step 1: Update FilterBar background and colors**

Replace the container div className:

```typescript
<div className="sticky top-0 z-30 bg-anthracite-900/80 backdrop-blur-md border-b border-violet/20 p-4">
```

**Step 2: Update input styling**

Replace Input className:

```typescript
className="pl-9 bg-anthracite-800/70 border-violet/30 text-foreground placeholder:text-muted-foreground focus:border-violet focus:ring-violet/30"
```

**Step 3: Update Select styling**

Replace SelectTrigger className:

```typescript
className="w-32 bg-anthracite-800/70 border-violet/30 text-foreground focus:border-violet focus:ring-violet/30"
```

Replace SelectContent className:

```typescript
className="bg-anthracite-900/95 border-violet/30"
```

Replace SelectItem className:

```typescript
className="text-foreground hover:bg-violet/20 focus:bg-violet/20"
```

**Step 4: Update badge styling**

Replace active badge className:

```typescript
isActive
  ? 'bg-violet/30 text-violet-light border-violet/70'
  : 'bg-anthracite-800/50 text-muted-foreground border-violet/20 hover:bg-violet/10 hover:border-violet/40'
```

**Step 5: Update clear button styling**

Replace Button className:

```typescript
className="h-7 bg-anthracite-800/50 text-foreground border border-violet/30 hover:bg-violet/20 hover:border-violet/50"
```

**Step 6: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 7: Commit**

```bash
git add components/feed/FilterBar.tsx
git commit -m "feat(articles): update FilterBar with violet theme styling"
```

---

## Task 14: Update Articles Page Background

**Files:**
- Modify: `app/articles/page.tsx`

**Step 1: Update background color**

Replace the main className:

```typescript
<main className="min-h-screen bg-anthracite-950">
```

**Step 2: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 3: Commit**

```bash
git add app/articles/page.tsx
git commit -m "feat(articles): update background to anthracite theme"
```

---

## Task 15: Add Reduced Motion Support to globals.css

**Files:**
- Modify: `app/globals.css`

**Step 1: Add prefers-reduced-motion media query**

Add at the end of the file:

```css
/* Accessibility: Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .card-3d-hover,
  .card-3d-hover:hover {
    transform: none !important;
  }

  .parallax-layer {
    transform: none !important;
  }

  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Step 2: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 3: Commit**

```bash
git add app/globals.css
git commit -m "feat(a11y): add reduced motion support for accessibility"
```

---

## Task 16: Update Sidebar and BottomNav Colors

**Files:**
- Modify: `components/layout/Sidebar.tsx`
- Modify: `components/layout/BottomNav.tsx`

**Step 1: Update Sidebar colors**

In `Sidebar.tsx`, replace background classes:

```typescript
className={cn(
  'hidden md:flex flex-col border-r border-violet/20 bg-anthracite-900 transition-all duration-300',
  collapsed ? 'w-16' : 'w-64'
)}
```

Border:
```typescript
className="flex items-center justify-between p-4 border-b border-violet/20"
```

Gradient:
```typescript
<h1 className="text-xl font-bold text-gradient-violet">
```

Footer:
```typescript
className="p-4 border-t border-violet/20 text-xs text-muted-foreground"
```

**Step 2: Update BottomNav colors**

In `BottomNav.tsx`, replace:

```typescript
<nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-anthracite-900 border-t border-violet/20">
```

Active state:
```typescript
isActive
  ? 'text-violet'
  : 'text-muted-foreground hover:text-foreground'
```

**Step 3: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 4: Commit**

```bash
git add components/layout/Sidebar.tsx components/layout/BottomNav.tsx
git commit -m "feat(layout): update navigation colors to violet theme"
```

---

## Task 17: Test Home Page in Browser

**Files:**
- None (manual testing)

**Step 1: Start dev server**

Run:
```bash
npm run dev
```

Expected: Dev server starts on port 3000 or 3001

**Step 2: Open browser and test**

Navigate to: `http://localhost:3000`

Test checklist:
- [ ] Parallax grid visible and animates on scroll
- [ ] Hero title has gradient and glow
- [ ] Best article card lifts and rotates on hover
- [ ] Best video card lifts and rotates on hover
- [ ] Stats section visible
- [ ] All animations smooth (60fps)
- [ ] No console errors

**Step 3: Test reduced motion**

In browser DevTools:
- Open DevTools (F12)
- Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows)
- Type "Emulate CSS prefers-reduced-motion"
- Select "reduce"
- Verify 3D effects disabled

---

## Task 18: Test Articles Page in Browser

**Files:**
- None (manual testing)

**Step 1: Navigate to articles page**

Navigate to: `http://localhost:3000/articles`

Test checklist:
- [ ] Background is anthracite
- [ ] Filter bar has violet borders
- [ ] Category badges have violet colors
- [ ] Article cards have violet accents
- [ ] Hover effects subtle (no 3D)
- [ ] Scroll smooth
- [ ] No console errors

**Step 2: Test responsiveness**

Resize browser:
- Desktop (1920px): All elements visible
- Tablet (768px): Layout adjusts
- Mobile (375px): Bottom nav appears

---

## Task 19: Performance Optimization

**Files:**
- Modify: `components/home/BestArticleCard3D.tsx`
- Modify: `components/home/BestVideoCard3D.tsx`

**Step 1: Add will-change to 3D cards**

In `BestArticleCard3D.tsx` and `BestVideoCard3D.tsx`, update motion.div:

```typescript
style={{
  transformStyle: 'preserve-3d',
  willChange: 'transform',
}}
```

**Step 2: Verify build**

Run:
```bash
npm run build
```

Expected: Build succeeds

**Step 3: Test performance**

Open Chrome DevTools → Performance tab
- Record while scrolling and hovering
- Check FPS stays above 55fps
- Check no layout shifts (CLS = 0)

**Step 4: Commit**

```bash
git add components/home/BestArticleCard3D.tsx components/home/BestVideoCard3D.tsx
git commit -m "perf: add will-change hint for 3D transforms"
```

---

## Task 20: Final Build and Lighthouse Test

**Files:**
- None (testing)

**Step 1: Production build**

Run:
```bash
npm run build
npm run start
```

Expected: Production server starts

**Step 2: Run Lighthouse**

In Chrome DevTools:
- Lighthouse tab
- Select "Desktop"
- Run audit

Target scores:
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90

**Step 3: Fix issues if any**

If Lighthouse < 90:
- Check bundle size
- Optimize images
- Review accessibility

**Step 4: Final commit**

```bash
git add .
git commit -m "feat: complete 3D theme redesign with violet/magenta palette"
```

---

## Done!

The 3D theme redesign is complete. Key features:
- ✅ Violet/magenta gradient color palette
- ✅ 3D card animations on home page
- ✅ Parallax grid background
- ✅ Minimal, fast articles page
- ✅ Reduced motion support
- ✅ Performance optimized (60fps)
