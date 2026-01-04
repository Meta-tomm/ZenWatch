# ZenWatch Cyberpunk Frontend Redesign

**Date**: 2026-01-04
**Status**: Design Complete
**Purpose**: Transform the ZenWatch frontend from basic UI to an immersive cyberpunk/Matrix-style tech interface with blue, black, and yellow color scheme

## Overview

A complete frontend redesign to create a visually stunning, tech-focused user experience inspired by cyberpunk aesthetics (Matrix, Tron, cyberpunk interfaces). The design features a hybrid landing approach with a command center hero section and cyberpunk-styled article feed below.

**Design Goals:**
- Create an immersive, futuristic tech aesthetic
- Maintain usability while adding visual wow factor
- Use blue, black, and yellow color scheme
- Implement smooth animations and effects
- Ensure responsive design and accessibility

**Visual Style:**
- Matrix-style falling characters background
- Glowing neon borders and accents
- Scan line effects
- Terminal/HUD-like elements
- Grid backgrounds with depth
- Glitch effects on interactions

## Color System & Theme

### Color Palette

**Primary Colors:**
```typescript
colors: {
  cyber: {
    blue: '#00D9FF',      // Neon cyan-blue - primary accent, glowing borders
    yellow: '#FFE600',    // Vibrant yellow - secondary accent, highlights
    black: '#0A0E27',     // Dark blue-black - main background
    gray: '#1A1F3A',      // Dark gray - card backgrounds
    green: '#00FF41',     // Matrix green - status indicators
  },
  text: {
    primary: '#E0E7FF',   // Light blue-white - main text
    muted: '#64748B',     // Gray-blue - secondary text
  }
}
```

**Shadow & Glow Effects:**
```typescript
boxShadow: {
  'neon-blue': '0 0 10px rgba(0, 217, 255, 0.5), 0 0 20px rgba(0, 217, 255, 0.3)',
  'neon-yellow': '0 0 10px rgba(255, 230, 0, 0.5), 0 0 20px rgba(255, 230, 0, 0.3)',
  'cyber': '0 0 30px rgba(0, 217, 255, 0.4)',
}
```

**Background Patterns:**
```typescript
backgroundImage: {
  'grid-pattern': 'linear-gradient(rgba(0, 217, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 217, 255, 0.1) 1px, transparent 1px)',
}
```

### Tailwind Config Update

**File:** `frontend/tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss"

const config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Cyberpunk palette
        cyber: {
          blue: '#00D9FF',
          yellow: '#FFE600',
          black: '#0A0E27',
          gray: '#1A1F3A',
          green: '#00FF41',
        },
        text: {
          primary: '#E0E7FF',
          muted: '#64748B',
        },
        // Keep existing shadcn colors for compatibility
        border: 'hsl(var(--border))',
        // ... rest of shadcn colors
      },
      boxShadow: {
        'neon-blue': '0 0 10px rgba(0, 217, 255, 0.5), 0 0 20px rgba(0, 217, 255, 0.3)',
        'neon-yellow': '0 0 10px rgba(255, 230, 0, 0.5), 0 0 20px rgba(255, 230, 0, 0.3)',
        'cyber': '0 0 30px rgba(0, 217, 255, 0.4)',
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(rgba(0, 217, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 217, 255, 0.03) 1px, transparent 1px)',
      },
      animation: {
        'glitch': 'glitch 0.3s infinite',
        'scan-line': 'scan-line 8s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'typing': 'typing 3s steps(40) 1s forwards',
        'blink-caret': 'blink-caret 0.75s step-end infinite',
      },
      keyframes: {
        glitch: {
          '0%, 100%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
        },
        'scan-line': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        'pulse-glow': {
          '0%, 100%': {
            boxShadow: '0 0 10px rgba(0, 217, 255, 0.4)'
          },
          '50%': {
            boxShadow: '0 0 20px rgba(0, 217, 255, 0.8), 0 0 30px rgba(0, 217, 255, 0.4)'
          },
        },
        typing: {
          'from': { width: '0' },
          'to': { width: '100%' },
        },
        'blink-caret': {
          '50%': { borderColor: 'transparent' },
        },
      },
    }
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config
```

### Global Styles

**File:** `frontend/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-cyber-black text-text-primary;
    background-image:
      linear-gradient(rgba(0, 217, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 217, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
  }
}

@layer utilities {
  /* Glitch text effect */
  .glitch-text {
    animation: glitch 0.3s infinite;
    animation-play-state: paused;
  }

  .glitch-text:hover {
    animation-play-state: running;
  }

  .glitch-hover:hover {
    animation: glitch 0.3s infinite;
  }

  /* Scan line effect */
  .scan-line {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg,
      transparent,
      rgba(0, 217, 255, 0.8),
      transparent
    );
    box-shadow: 0 0 20px rgba(0, 217, 255, 0.6);
    animation: scan-line 8s linear infinite;
    z-index: 100;
    pointer-events: none;
  }

  /* Typing animation */
  .typing-animation {
    overflow: hidden;
    border-right: 3px solid #FFE600;
    white-space: nowrap;
    animation:
      typing 3s steps(40) 1s forwards,
      blink-caret 0.75s step-end infinite;
  }

  /* Pulsing border glow */
  .pulse-border {
    animation: pulse-glow 2s ease-in-out infinite;
  }

  /* Neon text glow */
  .neon-text-blue {
    color: #00D9FF;
    text-shadow:
      0 0 10px rgba(0, 217, 255, 0.8),
      0 0 20px rgba(0, 217, 255, 0.6),
      0 0 30px rgba(0, 217, 255, 0.4);
  }

  .neon-text-yellow {
    color: #FFE600;
    text-shadow:
      0 0 10px rgba(255, 230, 0, 0.8),
      0 0 20px rgba(255, 230, 0, 0.6),
      0 0 30px rgba(255, 230, 0, 0.4);
  }
}
```

## Hero/Command Center Section

### Layout Structure

**Dimensions:**
- Height: 60vh (responsive)
- Full-width container
- Grid layout: 60% title / 40% metrics (desktop)
- Stacked layout on mobile

**Background Layers (z-index order):**
1. Matrix rain canvas (z-0)
2. Gradient overlay (z-1)
3. Content (z-10)
4. Scan line (z-100)

### Left Side: Animated Title & Tagline

**Component:** `components/home/AnimatedTitle.tsx`

```typescript
'use client';

import { motion } from 'framer-motion';
import { GlitchText } from '../cyberpunk/GlitchText';

export const AnimatedTitle = () => {
  return (
    <div className="space-y-6">
      {/* Main logo/title with glitch effect */}
      <motion.div
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-7xl md:text-8xl font-bold glitch-text">
          <span className="neon-text-blue">Zen</span>
          <span className="neon-text-yellow">Watch</span>
        </h1>
      </motion.div>

      {/* Typing animation tagline */}
      <motion.p
        className="text-2xl md:text-3xl text-text-muted typing-animation font-mono"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        Your AI-Powered Tech Radar_
      </motion.p>

      {/* Subtext */}
      <motion.p
        className="text-lg text-text-muted opacity-70 max-w-xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 0.7, y: 0 }}
        transition={{ delay: 1 }}
      >
        Real-time intelligence from{' '}
        <span className="text-cyber-blue">HackerNews</span>,{' '}
        <span className="text-cyber-yellow">Reddit</span>,{' '}
        <span className="text-cyber-green">Dev.to</span>
      </motion.p>
    </div>
  );
};
```

### Right Side: Live Metrics HUD

**Component:** `components/home/LiveMetrics.tsx`

```typescript
'use client';

import { motion } from 'framer-motion';
import { MetricCard } from '../cyberpunk/MetricCard';
import { Activity, Zap, TrendingUp, Target } from 'lucide-react';
import { useArticleStats } from '@/hooks/useArticleStats';

export const LiveMetrics = () => {
  const { data: stats, isLoading } = useArticleStats();

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    show: {
      opacity: 1,
      scale: 1,
      transition: {
        type: 'spring',
        stiffness: 200,
        damping: 15
      }
    }
  };

  if (isLoading) {
    return <MetricsLoadingSkeleton />;
  }

  return (
    <motion.div
      className="grid grid-cols-2 gap-4"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      <motion.div variants={itemVariants}>
        <MetricCard
          label="ARTICLES TODAY"
          value={stats.articlesToday}
          icon={Activity}
          glowColor="blue"
          animate={true}
        />
      </motion.div>

      <motion.div variants={itemVariants}>
        <MetricCard
          label="SOURCES ACTIVE"
          value={`${stats.activeSources}/${stats.totalSources}`}
          icon={Zap}
          glowColor="green"
          status="ONLINE"
        />
      </motion.div>

      <motion.div variants={itemVariants}>
        <MetricCard
          label="TOP TREND"
          value={stats.topTrend}
          icon={TrendingUp}
          glowColor="yellow"
        />
      </motion.div>

      <motion.div variants={itemVariants}>
        <MetricCard
          label="AVG SCORE"
          value={stats.avgScore.toFixed(1)}
          icon={Target}
          glowColor="blue"
        />
      </motion.div>
    </motion.div>
  );
};
```

**Component:** `components/cyberpunk/MetricCard.tsx`

```typescript
'use client';

import { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  glowColor: 'blue' | 'yellow' | 'green';
  status?: string;
  animate?: boolean;
}

export const MetricCard = ({
  label,
  value,
  icon: Icon,
  glowColor,
  status,
  animate = false
}: MetricCardProps) => {
  const glowColors = {
    blue: 'shadow-neon-blue border-cyber-blue',
    yellow: 'shadow-neon-yellow border-cyber-yellow',
    green: 'shadow-[0_0_10px_rgba(0,255,65,0.5)] border-cyber-green',
  };

  const textColors = {
    blue: 'text-cyber-blue',
    yellow: 'text-cyber-yellow',
    green: 'text-cyber-green',
  };

  return (
    <div className={`
      relative bg-cyber-gray border-2 ${glowColors[glowColor]}
      rounded-lg p-4 hover:${glowColors[glowColor]} transition-all
      ${animate ? 'pulse-border' : ''}
    `}>
      {/* Corner brackets */}
      <div className="absolute top-1 left-1 w-3 h-3 border-l-2 border-t-2 border-cyber-yellow" />
      <div className="absolute bottom-1 right-1 w-3 h-3 border-r-2 border-b-2 border-cyber-yellow" />

      {/* Icon */}
      <Icon className={`w-5 h-5 mb-2 ${textColors[glowColor]}`} />

      {/* Label */}
      <p className="text-xs text-text-muted font-mono tracking-wider uppercase">
        {label}
      </p>

      {/* Value */}
      <motion.p
        className={`text-2xl font-bold ${textColors[glowColor]} font-mono`}
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 200 }}
      >
        {value}
      </motion.p>

      {/* Optional status indicator */}
      {status && (
        <div className="flex items-center gap-1 mt-2">
          <div className="w-2 h-2 rounded-full bg-cyber-green animate-pulse" />
          <span className="text-xs text-cyber-green font-mono">{status}</span>
        </div>
      )}
    </div>
  );
};
```

### Main Hero Component

**Component:** `components/home/HeroSection.tsx`

```typescript
'use client';

import { motion } from 'framer-motion';
import { AnimatedTitle } from './AnimatedTitle';
import { LiveMetrics } from './LiveMetrics';
import { MatrixRain } from '../cyberpunk/MatrixRain';
import { ScanLine } from '../cyberpunk/ScanLine';
import { CornerBrackets } from '../cyberpunk/CornerBrackets';

export const HeroSection = () => {
  return (
    <section className="relative h-[60vh] flex items-center overflow-hidden border-b-2 border-cyber-blue/50">
      {/* Background effects */}
      <MatrixRain />
      <ScanLine />

      {/* Gradient overlay for readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-cyber-black/50 via-cyber-black/70 to-cyber-black z-1" />

      {/* Content container */}
      <div className="container mx-auto px-6 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 items-center">
          {/* Left: Title (60%) */}
          <motion.div
            className="lg:col-span-3"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <AnimatedTitle />
          </motion.div>

          {/* Right: Metrics (40%) */}
          <motion.div
            className="lg:col-span-2"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <LiveMetrics />
          </motion.div>
        </div>
      </div>

      {/* Top glowing border */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyber-blue to-transparent pulse-border" />

      {/* HUD corner brackets */}
      <CornerBrackets />
    </section>
  );
};
```

## Article Feed Cyberpunk Redesign

### Feed Container

**Visual Characteristics:**
- Dark background with subtle grid pattern
- Glowing divider between hero and feed
- Occasional scan line sweeps
- Smooth scroll with momentum

### Article Card Redesign

**Component:** `components/feed/ArticleCard.tsx` (Updated)

```typescript
'use client';

import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { ArrowUp, MessageSquare, Clock, ExternalLink, Zap } from 'lucide-react';
import { Article } from '@/types';
import { formatDistanceToNow } from 'date-fns';

interface ArticleCardProps {
  article: Article;
  index: number;
}

export const ArticleCard = ({ article, index }: ArticleCardProps) => {
  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    show: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 100,
        delay: index * 0.05 // Stagger effect
      }
    }
  };

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="show"
      className="relative group"
    >
      {/* Hover glow effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyber-blue/20 to-cyber-yellow/20
                      rounded-lg blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

      {/* Card content */}
      <div className="relative bg-cyber-gray border border-cyber-blue/30 rounded-lg p-6
                      hover:border-cyber-blue hover:shadow-neon-blue transition-all duration-300">

        {/* Top bar: Source badge + Score */}
        <div className="flex justify-between items-center mb-3">
          <Badge className="bg-cyber-blue/20 text-cyber-blue border-cyber-blue/50
                            font-mono text-xs tracking-wider uppercase">
            {article.source?.name || 'Unknown'}
          </Badge>

          <div className="flex items-center gap-2">
            <motion.span
              className="text-cyber-yellow font-bold text-xl font-mono
                         drop-shadow-[0_0_8px_rgba(255,230,0,0.6)]"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', delay: 0.2 }}
            >
              {article.score.toFixed(0)}
            </motion.span>
            <Zap className="w-4 h-4 text-cyber-yellow animate-pulse" />
          </div>
        </div>

        {/* Title with glitch on hover */}
        <h3 className="text-xl font-bold text-text-primary mb-3
                       group-hover:text-cyber-blue transition-colors
                       glitch-hover leading-tight">
          {article.title}
        </h3>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {article.tags?.slice(0, 4).map((tag, i) => (
            <span
              key={i}
              className="px-3 py-1 bg-cyber-black border border-cyber-blue/40
                         text-cyber-blue text-xs rounded-full font-mono
                         hover:bg-cyber-blue/10 hover:shadow-neon-blue transition-all cursor-pointer"
            >
              #{tag}
            </span>
          ))}
        </div>

        {/* Stats bar */}
        <div className="flex items-center gap-4 text-text-muted text-sm font-mono">
          <span className="flex items-center gap-1 hover:text-cyber-blue transition-colors">
            <ArrowUp className="w-4 h-4" /> {article.upvotes || 0}
          </span>
          <span className="flex items-center gap-1 hover:text-cyber-yellow transition-colors">
            <MessageSquare className="w-4 h-4" /> {article.comments_count || 0}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            {formatDistanceToNow(new Date(article.published_at), { addSuffix: true })}
          </span>
        </div>

        {/* Hover: Corner brackets appear */}
        <div className="absolute top-2 left-2 w-4 h-4 border-l-2 border-t-2
                        border-cyber-yellow opacity-0 group-hover:opacity-100
                        transition-opacity duration-300" />
        <div className="absolute top-2 right-2 w-4 h-4 border-r-2 border-t-2
                        border-cyber-yellow opacity-0 group-hover:opacity-100
                        transition-opacity duration-300" />
        <div className="absolute bottom-2 left-2 w-4 h-4 border-l-2 border-b-2
                        border-cyber-yellow opacity-0 group-hover:opacity-100
                        transition-opacity duration-300" />
        <div className="absolute bottom-2 right-2 w-4 h-4 border-r-2 border-b-2
                        border-cyber-yellow opacity-0 group-hover:opacity-100
                        transition-opacity duration-300" />

        {/* External link icon */}
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="absolute top-4 right-4 opacity-0 group-hover:opacity-100
                     text-cyber-blue hover:text-cyber-yellow transition-all"
        >
          <ExternalLink className="w-5 h-5" />
        </a>
      </div>
    </motion.div>
  );
};
```

### Filter Bar Redesign

**Component:** `components/feed/FilterBar.tsx` (Updated)

```typescript
'use client';

import { motion } from 'framer-motion';
import { Search, SlidersHorizontal } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

export const FilterBar = () => {
  const categories = ['All', 'AI', 'Web3', 'DevTools', 'Cloud'];
  const sources = ['HackerNews', 'Reddit', 'Dev.to'];

  return (
    <div className="sticky top-0 z-50 bg-cyber-black/95 backdrop-blur-sm
                    border-b border-cyber-blue/30 p-4 mb-6">
      <div className="container mx-auto">
        <div className="flex flex-col md:flex-row gap-4 items-center">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cyber-blue" />
            <Input
              placeholder="Search articles..."
              className="pl-10 bg-cyber-gray border-cyber-blue/40
                         text-text-primary placeholder:text-text-muted
                         focus:border-cyber-blue focus:shadow-neon-blue
                         font-mono"
            />
          </div>

          {/* Category pills */}
          <div className="flex gap-2 flex-wrap">
            {categories.map((cat) => (
              <Badge
                key={cat}
                variant="outline"
                className="cursor-pointer bg-cyber-black border-cyber-blue/40
                           text-cyber-blue hover:bg-cyber-blue/20
                           hover:shadow-neon-blue transition-all font-mono"
              >
                {cat}
              </Badge>
            ))}
          </div>

          {/* Filters button */}
          <button className="flex items-center gap-2 px-4 py-2
                             bg-cyber-gray border border-cyber-yellow/40
                             text-cyber-yellow rounded-lg
                             hover:bg-cyber-yellow/10 hover:shadow-neon-yellow
                             transition-all font-mono">
            <SlidersHorizontal className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>
      </div>
    </div>
  );
};
```

## Cyberpunk Effect Components

### Matrix Rain Background

**Component:** `components/cyberpunk/MatrixRain.tsx`

```typescript
'use client';

import { useEffect, useRef } from 'react';

export const MatrixRain = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Characters to use
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    const fontSize = 14;
    const columns = canvas.width / fontSize;

    // Track drop position for each column
    const drops: number[] = [];
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -100; // Start with random offset
    }

    // Animation loop
    const draw = () => {
      // Fade effect (semi-transparent black)
      ctx.fillStyle = 'rgba(10, 14, 39, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw characters
      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        // Random character
        const char = chars[Math.floor(Math.random() * chars.length)];

        // Color: mix of blue and green
        const colorValue = Math.random();
        if (colorValue > 0.98) {
          ctx.fillStyle = '#FFE600'; // Rare yellow
        } else if (colorValue > 0.9) {
          ctx.fillStyle = '#00FF41'; // Green
        } else {
          ctx.fillStyle = '#00D9FF'; // Blue
        }

        // Draw character
        const x = i * fontSize;
        const y = drops[i] * fontSize;
        ctx.fillText(char, x, y);

        // Reset drop when it goes off screen
        if (y > canvas.height && Math.random() > 0.95) {
          drops[i] = 0;
        }

        // Move drop down
        drops[i]++;
      }
    };

    const interval = setInterval(draw, 50);

    // Cleanup
    return () => clearInterval(interval);
  }, []);

  // Respect reduced motion preference
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (prefersReducedMotion) return null;

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none opacity-30"
      style={{ zIndex: 0 }}
    />
  );
};
```

### Scan Line Effect

**Component:** `components/cyberpunk/ScanLine.tsx`

```typescript
'use client';

export const ScanLine = () => {
  // Respect reduced motion preference
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (prefersReducedMotion) return null;

  return (
    <div className="scan-line" />
  );
};
```

### Corner Brackets

**Component:** `components/cyberpunk/CornerBrackets.tsx`

```typescript
'use client';

export const CornerBrackets = () => {
  const bracketSize = 40;
  const thickness = 3;
  const color = '#FFE600';

  return (
    <>
      {/* Top-left */}
      <div
        className="absolute top-4 left-4 border-l-[3px] border-t-[3px] border-cyber-yellow"
        style={{ width: bracketSize, height: bracketSize }}
      />

      {/* Top-right */}
      <div
        className="absolute top-4 right-4 border-r-[3px] border-t-[3px] border-cyber-yellow"
        style={{ width: bracketSize, height: bracketSize }}
      />

      {/* Bottom-left */}
      <div
        className="absolute bottom-4 left-4 border-l-[3px] border-b-[3px] border-cyber-yellow"
        style={{ width: bracketSize, height: bracketSize }}
      />

      {/* Bottom-right */}
      <div
        className="absolute bottom-4 right-4 border-r-[3px] border-b-[3px] border-cyber-yellow"
        style={{ width: bracketSize, height: bracketSize }}
      />
    </>
  );
};
```

### Glitch Text Component

**Component:** `components/cyberpunk/GlitchText.tsx`

```typescript
'use client';

interface GlitchTextProps {
  children: React.ReactNode;
  className?: string;
}

export const GlitchText = ({ children, className = '' }: GlitchTextProps) => {
  return (
    <span className={`glitch-text ${className}`}>
      {children}
    </span>
  );
};
```

## Updated Page Structure

**File:** `frontend/app/page.tsx`

```typescript
import { HeroSection } from '@/components/home/HeroSection';
import { FilterBar } from '@/components/feed/FilterBar';
import { ArticleFeed } from '@/components/feed/ArticleFeed';

export default function Home() {
  return (
    <div className="relative min-h-screen">
      {/* Hero section with command center */}
      <HeroSection />

      {/* Glowing divider between hero and feed */}
      <div className="h-px bg-gradient-to-r from-transparent via-cyber-blue to-transparent opacity-50" />

      {/* Main content area */}
      <div className="container mx-auto px-6 py-8">
        <FilterBar />
        <ArticleFeed />
      </div>
    </div>
  );
}
```

## Framer Motion Configurations

**File:** `frontend/lib/animations.ts`

```typescript
import { Variants } from 'framer-motion';

// Page transition animations
export const pageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: 'easeOut'
    }
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3
    }
  }
};

// Stagger container for article cards
export const containerVariants: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

// Individual card animation
export const cardVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
    scale: 0.95
  },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 15
    }
  }
};

// Metric counter animation
export const counterVariants: Variants = {
  initial: {
    scale: 0.5,
    opacity: 0
  },
  animate: {
    scale: 1,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 200,
      damping: 15
    }
  }
};

// Fade in from side
export const fadeInLeft: Variants = {
  initial: {
    opacity: 0,
    x: -50
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.8,
      ease: 'easeOut'
    }
  }
};

export const fadeInRight: Variants = {
  initial: {
    opacity: 0,
    x: 50
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.8,
      ease: 'easeOut'
    }
  }
};
```

## Component File Structure

```
frontend/
├── app/
│   ├── globals.css                  # Updated with cyberpunk styles
│   ├── page.tsx                     # Updated with HeroSection
│   └── layout.tsx                   # Existing (no changes)
│
├── components/
│   ├── cyberpunk/                   # NEW: Cyberpunk effect components
│   │   ├── MatrixRain.tsx          # Canvas matrix background
│   │   ├── ScanLine.tsx            # Sweeping scan line
│   │   ├── GlitchText.tsx          # Reusable glitch text
│   │   ├── MetricCard.tsx          # HUD metric card
│   │   ├── CyberBadge.tsx          # Styled badge
│   │   └── CornerBrackets.tsx      # HUD corner decorations
│   │
│   ├── home/                        # NEW: Home page components
│   │   ├── HeroSection.tsx         # Main hero container
│   │   ├── AnimatedTitle.tsx       # Title with glitch
│   │   └── LiveMetrics.tsx         # Metrics grid
│   │
│   ├── feed/                        # UPDATED: Feed components
│   │   ├── ArticleCard.tsx         # Redesigned with cyber style
│   │   ├── FilterBar.tsx           # Updated with glowing pills
│   │   └── ArticleFeed.tsx         # Updated animations
│   │
│   └── ui/                          # Existing shadcn components
│       └── ...                      # Keep as-is
│
├── lib/
│   ├── animations.ts                # NEW: Framer Motion configs
│   └── ...                          # Existing files
│
├── hooks/
│   └── useArticleStats.ts           # NEW: Fetch real-time stats
│
└── tailwind.config.ts               # UPDATED: Cyber colors
```

## Dependencies

**Install Required Packages:**

```bash
npm install framer-motion
```

**Existing Dependencies (already installed):**
- `lucide-react` - Icons
- `tailwindcss-animate` - Animation utilities
- `@tanstack/react-query` - Data fetching

**Optional Enhancements:**
```bash
npm install @tabler/icons-react  # More cyberpunk-style icons
```

## Implementation Plan

### Week 1: Foundation & Theme Setup

**Tasks:**
1. Update `tailwind.config.ts` with cyber color palette
2. Update `globals.css` with animations and grid background
3. Test color scheme in existing components
4. Create `components/cyberpunk/` folder structure
5. Build base cyberpunk components:
   - GlitchText.tsx
   - CornerBrackets.tsx
   - CyberBadge.tsx (if needed)
6. Test animations in isolation

**Deliverables:**
- [ ] Tailwind config updated
- [ ] Global styles with animations
- [ ] Base cyberpunk components working
- [ ] Colors tested and validated

### Week 2: Hero Section Implementation

**Tasks:**
1. Create `components/home/` folder
2. Build MatrixRain.tsx canvas component
3. Build ScanLine.tsx effect
4. Build AnimatedTitle.tsx with glitch effects
5. Create useArticleStats hook for real-time data
6. Build MetricCard.tsx component
7. Build LiveMetrics.tsx grid
8. Assemble HeroSection.tsx
9. Add Framer Motion page transitions
10. Test responsive design (mobile/tablet/desktop)

**Deliverables:**
- [ ] Working matrix rain background
- [ ] Animated hero section
- [ ] Live metrics displaying real data
- [ ] Responsive across all breakpoints
- [ ] Smooth page transitions

### Week 3: Feed Redesign

**Tasks:**
1. Redesign ArticleCard.tsx with cyberpunk styling
2. Add hover effects (glowing borders, corner brackets)
3. Update FilterBar.tsx with glowing pill buttons
4. Implement stagger animations on article feed
5. Add loading states with cyber spinners
6. Create custom scrollbar styling
7. Test infinite scroll behavior
8. Polish micro-interactions

**Deliverables:**
- [ ] Article cards with cyberpunk design
- [ ] Smooth hover effects
- [ ] Filter bar with glow effects
- [ ] Stagger animations working
- [ ] Loading states polished

### Week 4: Polish, Optimize & Accessibility

**Tasks:**
1. Fine-tune animation timing and easing
2. Optimize canvas performance
   - Throttle FPS on mobile
   - Reduce particle count if needed
3. Add reduced motion support
4. Ensure WCAG AA color contrast
5. Test keyboard navigation
6. Add screen reader labels
7. Performance testing (Lighthouse)
8. Cross-browser testing
9. Mobile polish (touch interactions)
10. Final QA pass

**Deliverables:**
- [ ] All animations at 60fps (desktop)
- [ ] Reduced motion support working
- [ ] WCAG AA compliant
- [ ] Lighthouse score >90
- [ ] Works on all major browsers
- [ ] Mobile experience polished

## Performance Considerations

### Reduced Motion Support

**Respect User Preferences:**

```typescript
// Check for reduced motion preference
const prefersReducedMotion =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Conditionally disable heavy animations
const shouldAnimate = !prefersReducedMotion;

// Example in component
if (prefersReducedMotion) {
  return <StaticVersion />;
}

return <AnimatedVersion />;
```

### Canvas Optimization

**Adaptive Frame Rate:**

```typescript
// Adjust FPS based on device
const isMobile = window.innerWidth < 768;
const targetFPS = isMobile ? 30 : 60;
const frameInterval = 1000 / targetFPS;

let lastFrameTime = 0;

const animate = (currentTime: number) => {
  if (currentTime - lastFrameTime >= frameInterval) {
    // Draw frame
    lastFrameTime = currentTime;
  }
  requestAnimationFrame(animate);
};
```

**Throttle on Low-End Devices:**

```typescript
// Detect performance capability
const isLowEndDevice = navigator.hardwareConcurrency <= 4;

if (isLowEndDevice) {
  // Reduce particle count
  // Lower FPS
  // Simplify effects
}
```

### Bundle Size

**Code Splitting:**

```typescript
// Lazy load heavy components
import dynamic from 'next/dynamic';

const MatrixRain = dynamic(
  () => import('@/components/cyberpunk/MatrixRain'),
  { ssr: false }
);
```

## Accessibility Checklist

**Color Contrast:**
- [ ] Cyber blue on black meets WCAG AA (4.5:1 minimum)
- [ ] Yellow text on black meets WCAG AA
- [ ] All text is readable

**Motion:**
- [ ] `prefers-reduced-motion` support implemented
- [ ] Heavy animations disabled for sensitive users
- [ ] Page remains functional without animations

**Keyboard Navigation:**
- [ ] All interactive elements are keyboard accessible
- [ ] Focus states are visible (glowing outline)
- [ ] Tab order is logical

**Screen Readers:**
- [ ] All images have alt text
- [ ] Decorative elements have `aria-hidden="true"`
- [ ] Interactive elements have proper labels
- [ ] Semantic HTML used throughout

**Testing:**
- [ ] Test with screen reader (NVDA/JAWS/VoiceOver)
- [ ] Test keyboard-only navigation
- [ ] Test with Windows High Contrast mode
- [ ] Run axe DevTools audit

## Testing Strategy

### Visual Regression Testing

**Key Scenarios:**
1. Hero section loads correctly
2. Matrix rain renders
3. Article cards display properly
4. Hover effects work
5. Mobile responsive layouts

### Performance Testing

**Metrics to Track:**
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Canvas FPS: 60fps desktop, 30fps mobile
- Bundle size: Monitor framer-motion impact

**Tools:**
- Chrome DevTools Performance tab
- Lighthouse CI
- WebPageTest
- React DevTools Profiler

### Browser Compatibility

**Test on:**
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile Safari (iOS)
- Chrome Mobile (Android)

### Animation Smoothness

**Checklist:**
- [ ] All animations run at 60fps (desktop)
- [ ] No jank during scroll
- [ ] Matrix rain doesn't cause lag
- [ ] Page transitions are smooth
- [ ] Hover effects are instant

## Success Metrics

**Technical:**
- [ ] All components built and functional
- [ ] Zero console errors
- [ ] Lighthouse Performance >90
- [ ] Lighthouse Accessibility >95
- [ ] All animations smooth (60fps)
- [ ] Works on mobile/tablet/desktop

**Design:**
- [ ] Cyberpunk aesthetic achieved
- [ ] Blue/black/yellow color scheme consistent
- [ ] Visual hierarchy clear
- [ ] Interactive elements obvious
- [ ] Hover states provide feedback

**User Experience:**
- [ ] Page loads quickly
- [ ] Animations enhance, don't distract
- [ ] Content is readable
- [ ] Navigation is intuitive
- [ ] Works with keyboard only
- [ ] Works with screen reader

## Files to Create/Modify

### New Files:
```
frontend/components/cyberpunk/MatrixRain.tsx
frontend/components/cyberpunk/ScanLine.tsx
frontend/components/cyberpunk/GlitchText.tsx
frontend/components/cyberpunk/MetricCard.tsx
frontend/components/cyberpunk/CornerBrackets.tsx
frontend/components/home/HeroSection.tsx
frontend/components/home/AnimatedTitle.tsx
frontend/components/home/LiveMetrics.tsx
frontend/hooks/useArticleStats.ts
frontend/lib/animations.ts
```

### Modified Files:
```
frontend/tailwind.config.ts          # Add cyber colors
frontend/app/globals.css             # Add animations
frontend/app/page.tsx                # Add HeroSection
frontend/components/feed/ArticleCard.tsx    # Cyber redesign
frontend/components/feed/FilterBar.tsx      # Cyber redesign
frontend/components/feed/ArticleFeed.tsx    # Add stagger
```

## Next Steps

1. Review and approve this design
2. Start Week 1 implementation (foundation)
3. Iterate on hero section
4. Test with real data
5. Polish and optimize

---

**Estimated Timeline:** 4 weeks
**Risk Level:** Medium (canvas animations require testing)
**Dependencies:** framer-motion
**Accessibility:** High priority (reduced motion, contrast)

**Last Updated:** 2026-01-04
