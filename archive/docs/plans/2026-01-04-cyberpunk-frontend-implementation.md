# Cyberpunk Frontend Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform ZenWatch frontend into an immersive cyberpunk/Matrix-style interface with blue, black, and yellow color scheme, featuring a command center hero section and redesigned article feed.

**Architecture:** Hybrid animation approach using Framer Motion for UI animations and HTML5 Canvas for background effects (matrix rain). Component-based architecture with cyberpunk effect components separated into their own module.

**Tech Stack:** Next.js 14, React, TypeScript, Tailwind CSS, Framer Motion, HTML5 Canvas

---

## Phase 1: Foundation & Theme Setup

### Task 1: Install Dependencies

**Files:**
- Modify: `frontend/package.json`

**Step 1: Install framer-motion**

```bash
cd frontend
npm install framer-motion
```

Expected output: `added 1 package`

**Step 2: Verify installation**

```bash
npm list framer-motion
```

Expected: Shows framer-motion version

**Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "chore(frontend): install framer-motion for animations"
```

---

### Task 2: Update Tailwind Config with Cyberpunk Colors

**Files:**
- Modify: `frontend/tailwind.config.ts`

**Step 1: Back up current config**

```bash
cp frontend/tailwind.config.ts frontend/tailwind.config.ts.backup
```

**Step 2: Update Tailwind config**

Replace the `theme.extend.colors` section:

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
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px'
      }
    },
    extend: {
      screens: {
        xs: '375px',
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px'
      },
      colors: {
        // Cyberpunk color palette
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
        // Keep existing shadcn colors
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
        }
      },
      boxShadow: {
        'neon-blue': '0 0 10px rgba(0, 217, 255, 0.5), 0 0 20px rgba(0, 217, 255, 0.3)',
        'neon-yellow': '0 0 10px rgba(255, 230, 0, 0.5), 0 0 20px rgba(255, 230, 0, 0.3)',
        'neon-green': '0 0 10px rgba(0, 255, 65, 0.5), 0 0 20px rgba(0, 255, 65, 0.3)',
        'cyber': '0 0 30px rgba(0, 217, 255, 0.4)',
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(rgba(0, 217, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 217, 255, 0.03) 1px, transparent 1px)',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },
      keyframes: {
        'accordion-down': {
          from: {
            height: '0'
          },
          to: {
            height: 'var(--radix-accordion-content-height)'
          }
        },
        'accordion-up': {
          from: {
            height: 'var(--radix-accordion-content-height)'
          },
          to: {
            height: '0'
          }
        },
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
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'glitch': 'glitch 0.3s infinite',
        'scan-line': 'scan-line 8s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'typing': 'typing 3s steps(40) 1s forwards',
        'blink-caret': 'blink-caret 0.75s step-end infinite',
      }
    }
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config
```

**Step 3: Test the config**

```bash
npm run dev
```

Expected: No errors, dev server starts

**Step 4: Remove backup**

```bash
rm frontend/tailwind.config.ts.backup
```

**Step 5: Commit**

```bash
git add frontend/tailwind.config.ts
git commit -m "feat(frontend): add cyberpunk color palette and animations to Tailwind config"
```

---

### Task 3: Update Global CSS with Cyberpunk Styles

**Files:**
- Modify: `frontend/app/globals.css`

**Step 1: Backup current globals.css**

```bash
cp frontend/app/globals.css frontend/app/globals.css.backup
```

**Step 2: Update globals.css**

Add the following after the existing Tailwind directives:

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

  .neon-text-green {
    color: #00FF41;
    text-shadow:
      0 0 10px rgba(0, 255, 65, 0.8),
      0 0 20px rgba(0, 255, 65, 0.6),
      0 0 30px rgba(0, 255, 65, 0.4);
  }
}
```

**Step 3: Test the styles**

```bash
npm run dev
```

Visit http://localhost:3000 - background should now be dark blue-black with subtle grid

**Step 4: Remove backup**

```bash
rm frontend/app/globals.css.backup
```

**Step 5: Commit**

```bash
git add frontend/app/globals.css
git commit -m "feat(frontend): add cyberpunk global styles and animations"
```

---

## Phase 2: Cyberpunk Effect Components

### Task 4: Create Cyberpunk Components Directory

**Files:**
- Create: `frontend/components/cyberpunk/` (directory)

**Step 1: Create directory**

```bash
mkdir -p frontend/components/cyberpunk
```

**Step 2: Verify directory**

```bash
ls -la frontend/components/
```

Expected: cyberpunk directory exists

**Step 3: Commit**

```bash
git add frontend/components/cyberpunk/.gitkeep
git commit -m "chore(frontend): create cyberpunk components directory"
```

Note: Git doesn't track empty directories, so we'll commit with the first file instead.

---

### Task 5: Create ScanLine Component

**Files:**
- Create: `frontend/components/cyberpunk/ScanLine.tsx`

**Step 1: Create ScanLine component**

```typescript
'use client';

export const ScanLine = () => {
  // Respect reduced motion preference
  if (typeof window !== 'undefined') {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return null;
  }

  return (
    <div className="scan-line" />
  );
};
```

**Step 2: Test import**

Create a test file to verify it compiles:

```bash
echo "import { ScanLine } from './ScanLine';" > frontend/components/cyberpunk/test.ts
npx tsc --noEmit frontend/components/cyberpunk/test.ts
rm frontend/components/cyberpunk/test.ts
```

Expected: No TypeScript errors

**Step 3: Commit**

```bash
git add frontend/components/cyberpunk/ScanLine.tsx
git commit -m "feat(frontend): add ScanLine cyberpunk effect component"
```

---

### Task 6: Create CornerBrackets Component

**Files:**
- Create: `frontend/components/cyberpunk/CornerBrackets.tsx`

**Step 1: Create CornerBrackets component**

```typescript
'use client';

interface CornerBracketsProps {
  size?: number;
  color?: string;
  className?: string;
}

export const CornerBrackets = ({
  size = 40,
  color = 'border-cyber-yellow',
  className = ''
}: CornerBracketsProps) => {
  return (
    <>
      {/* Top-left */}
      <div
        className={`absolute top-4 left-4 border-l-[3px] border-t-[3px] ${color} ${className}`}
        style={{ width: size, height: size }}
      />

      {/* Top-right */}
      <div
        className={`absolute top-4 right-4 border-r-[3px] border-t-[3px] ${color} ${className}`}
        style={{ width: size, height: size }}
      />

      {/* Bottom-left */}
      <div
        className={`absolute bottom-4 left-4 border-l-[3px] border-b-[3px] ${color} ${className}`}
        style={{ width: size, height: size }}
      />

      {/* Bottom-right */}
      <div
        className={`absolute bottom-4 right-4 border-r-[3px] border-b-[3px] ${color} ${className}`}
        style={{ width: size, height: size }}
      />
    </>
  );
};
```

**Step 2: Test TypeScript**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/components/cyberpunk/CornerBrackets.tsx
git commit -m "feat(frontend): add CornerBrackets HUD decoration component"
```

---

### Task 7: Create GlitchText Component

**Files:**
- Create: `frontend/components/cyberpunk/GlitchText.tsx`

**Step 1: Create GlitchText component**

```typescript
'use client';

interface GlitchTextProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export const GlitchText = ({
  children,
  className = '',
  hover = false
}: GlitchTextProps) => {
  const glitchClass = hover ? 'glitch-hover' : 'glitch-text';

  return (
    <span className={`${glitchClass} ${className}`}>
      {children}
    </span>
  );
};
```

**Step 2: Test TypeScript**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/components/cyberpunk/GlitchText.tsx
git commit -m "feat(frontend): add GlitchText animation component"
```

---

### Task 8: Create MatrixRain Component

**Files:**
- Create: `frontend/components/cyberpunk/MatrixRain.tsx`

**Step 1: Create MatrixRain component**

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
    const setCanvasSize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    setCanvasSize();
    window.addEventListener('resize', setCanvasSize);

    // Characters to use (mix of tech symbols and katakana)
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);

    // Track drop position for each column
    const drops: number[] = [];
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -100;
    }

    // Animation loop
    let animationId: number;
    const draw = () => {
      // Fade effect
      ctx.fillStyle = 'rgba(10, 14, 39, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)];

        // Color variation
        const colorValue = Math.random();
        if (colorValue > 0.98) {
          ctx.fillStyle = '#FFE600'; // Yellow
        } else if (colorValue > 0.9) {
          ctx.fillStyle = '#00FF41'; // Green
        } else {
          ctx.fillStyle = '#00D9FF'; // Blue
        }

        const x = i * fontSize;
        const y = drops[i] * fontSize;
        ctx.fillText(char, x, y);

        if (y > canvas.height && Math.random() > 0.95) {
          drops[i] = 0;
        }

        drops[i]++;
      }

      animationId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', setCanvasSize);
    };
  }, []);

  // Respect reduced motion
  if (typeof window !== 'undefined') {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return null;
  }

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none opacity-30"
      style={{ zIndex: 0 }}
    />
  );
};
```

**Step 2: Test TypeScript**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/components/cyberpunk/MatrixRain.tsx
git commit -m "feat(frontend): add MatrixRain canvas background effect"
```

---

### Task 9: Create MetricCard Component

**Files:**
- Create: `frontend/components/cyberpunk/MetricCard.tsx`

**Step 1: Create MetricCard component**

```typescript
'use client';

import { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  glowColor?: 'blue' | 'yellow' | 'green';
  status?: string;
  animate?: boolean;
}

export const MetricCard = ({
  label,
  value,
  icon: Icon,
  glowColor = 'blue',
  status,
  animate = false
}: MetricCardProps) => {
  const glowColors = {
    blue: 'shadow-neon-blue border-cyber-blue',
    yellow: 'shadow-neon-yellow border-cyber-yellow',
    green: 'shadow-neon-green border-cyber-green',
  };

  const textColors = {
    blue: 'text-cyber-blue',
    yellow: 'text-cyber-yellow',
    green: 'text-cyber-green',
  };

  return (
    <div className={`
      relative bg-cyber-gray border-2 ${glowColors[glowColor]}
      rounded-lg p-4 transition-all
      ${animate ? 'pulse-border' : ''}
    `}>
      {/* Corner brackets */}
      <div className="absolute top-1 left-1 w-3 h-3 border-l-2 border-t-2 border-cyber-yellow" />
      <div className="absolute bottom-1 right-1 w-3 h-3 border-r-2 border-b-2 border-cyber-yellow" />

      {/* Icon */}
      <Icon className={`w-5 h-5 mb-2 ${textColors[glowColor]}`} />

      {/* Label */}
      <p className="text-xs text-text-muted font-mono tracking-wider uppercase mb-1">
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

      {/* Optional status */}
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

**Step 2: Test TypeScript**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/components/cyberpunk/MetricCard.tsx
git commit -m "feat(frontend): add MetricCard HUD component"
```

---

### Task 10: Create Cyberpunk Index Export

**Files:**
- Create: `frontend/components/cyberpunk/index.ts`

**Step 1: Create index file**

```typescript
export { ScanLine } from './ScanLine';
export { CornerBrackets } from './CornerBrackets';
export { GlitchText } from './GlitchText';
export { MatrixRain } from './MatrixRain';
export { MetricCard } from './MetricCard';
```

**Step 2: Test imports**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/components/cyberpunk/index.ts
git commit -m "feat(frontend): add cyberpunk components index export"
```

---

## Phase 3: Hero Section Components

### Task 11: Create Home Components Directory

**Files:**
- Create: `frontend/components/home/` (directory)

**Step 1: Create directory**

```bash
mkdir -p frontend/components/home
```

**Step 2: Verify**

```bash
ls -la frontend/components/
```

Expected: home directory exists

---

### Task 12: Create Framer Motion Animation Configs

**Files:**
- Create: `frontend/lib/animations.ts`

**Step 1: Create animations file**

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

// Stagger container for cards
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

// Card animation
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

// Fade in from left
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

// Fade in from right
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

**Step 2: Test TypeScript**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/lib/animations.ts
git commit -m "feat(frontend): add Framer Motion animation configurations"
```

---

### Task 13: Create AnimatedTitle Component

**Files:**
- Create: `frontend/components/home/AnimatedTitle.tsx`

**Step 1: Create AnimatedTitle component**

```typescript
'use client';

import { motion } from 'framer-motion';

export const AnimatedTitle = () => {
  return (
    <div className="space-y-6">
      {/* Main logo/title */}
      <motion.div
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold glitch-text">
          <span className="neon-text-blue">Zen</span>
          <span className="neon-text-yellow">Watch</span>
        </h1>
      </motion.div>

      {/* Typing animation tagline */}
      <motion.p
        className="text-xl md:text-2xl lg:text-3xl text-text-muted typing-animation font-mono"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        Your AI-Powered Tech Radar_
      </motion.p>

      {/* Subtext */}
      <motion.p
        className="text-base md:text-lg text-text-muted opacity-70 max-w-xl"
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

**Step 2: Test TypeScript**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/components/home/AnimatedTitle.tsx
git commit -m "feat(frontend): add AnimatedTitle hero component"
```

---

### Task 14: Create LiveMetrics Component (Static Version)

**Files:**
- Create: `frontend/components/home/LiveMetrics.tsx`

**Step 1: Create LiveMetrics component with mock data**

```typescript
'use client';

import { motion } from 'framer-motion';
import { MetricCard } from '../cyberpunk/MetricCard';
import { Activity, Zap, TrendingUp, Target } from 'lucide-react';

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

export const LiveMetrics = () => {
  // TODO: Replace with real data from API
  const stats = {
    articlesToday: 847,
    activeSources: 3,
    totalSources: 3,
    topTrend: 'Rust',
    avgScore: 72.4
  };

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

**Step 2: Test TypeScript**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/components/home/LiveMetrics.tsx
git commit -m "feat(frontend): add LiveMetrics component with mock data"
```

---

### Task 15: Create HeroSection Component

**Files:**
- Create: `frontend/components/home/HeroSection.tsx`

**Step 1: Create HeroSection component**

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
    <section className="relative h-[60vh] min-h-[500px] flex items-center overflow-hidden border-b-2 border-cyber-blue/50">
      {/* Background effects */}
      <MatrixRain />
      <ScanLine />

      {/* Gradient overlay for readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-cyber-black/50 via-cyber-black/70 to-cyber-black z-1" />

      {/* Content container */}
      <div className="container mx-auto px-6 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-12 items-center">
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

**Step 2: Test TypeScript**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/components/home/HeroSection.tsx
git commit -m "feat(frontend): add HeroSection main component"
```

---

### Task 16: Update Home Page to Use HeroSection

**Files:**
- Modify: `frontend/app/page.tsx`

**Step 1: Backup current page**

```bash
cp frontend/app/page.tsx frontend/app/page.tsx.backup
```

**Step 2: Update page.tsx**

```typescript
import { HeroSection } from '@/components/home/HeroSection';
import { FilterBar } from '@/components/feed/FilterBar';
import { ArticleFeed } from '@/components/feed/ArticleFeed';
import { ArticleModal } from '@/components/feed/ArticleModal';

export default function Home() {
  return (
    <div className="relative min-h-screen">
      {/* Hero section */}
      <HeroSection />

      {/* Glowing divider */}
      <div className="h-px bg-gradient-to-r from-transparent via-cyber-blue to-transparent opacity-50" />

      {/* Main content */}
      <div className="flex flex-col h-full">
        <FilterBar />
        <ArticleFeed />
      </div>

      <ArticleModal />
    </div>
  );
}
```

**Step 3: Test the page**

```bash
npm run dev
```

Visit http://localhost:3000 and verify:
- Hero section displays
- Matrix rain animates in background
- Scan line moves across screen
- Title has glitch effect on hover
- Metrics cards display with animations
- Feed still works below

**Step 4: Remove backup**

```bash
rm frontend/app/page.tsx.backup
```

**Step 5: Commit**

```bash
git add frontend/app/page.tsx
git commit -m "feat(frontend): integrate HeroSection into home page"
```

---

## Phase 4: Article Feed Cyberpunk Redesign (Preview)

### Task 17: Update ArticleCard with Cyberpunk Styling

**Files:**
- Modify: `frontend/components/feed/ArticleCard.tsx`

**Step 1: Read current ArticleCard**

```bash
cat frontend/components/feed/ArticleCard.tsx
```

**Step 2: Backup current version**

```bash
cp frontend/components/feed/ArticleCard.tsx frontend/components/feed/ArticleCard.tsx.backup
```

**Step 3: Update ArticleCard with cyberpunk styling**

Note: This is a large update. The component should:
- Add glowing border on hover
- Show score with neon yellow glow
- Use cyber-themed badges
- Add corner brackets on hover
- Use font-mono for tech feel

Replace the entire file content with the cyberpunk version from the design doc.

**Step 4: Test the updated card**

```bash
npm run dev
```

Visit http://localhost:3000 and verify article cards have cyberpunk styling

**Step 5: Remove backup if successful**

```bash
rm frontend/components/feed/ArticleCard.tsx.backup
```

**Step 6: Commit**

```bash
git add frontend/components/feed/ArticleCard.tsx
git commit -m "feat(frontend): redesign ArticleCard with cyberpunk styling"
```

---

## Testing & Validation

### Task 18: Test Accessibility

**Step 1: Test reduced motion**

In browser DevTools:
1. Open DevTools
2. Cmd/Ctrl + Shift + P
3. Type "Emulate CSS prefers-reduced-motion"
4. Select "prefers-reduced-motion: reduce"

Expected: Matrix rain and scan line should not appear

**Step 2: Test keyboard navigation**

Press Tab repeatedly through the page
Expected: Focus states are visible with glowing outlines

**Step 3: Test color contrast**

Use browser extension or DevTools to check:
- Cyber blue on black: Should meet WCAG AA
- Yellow on black: Should meet WCAG AA
- All text readable

**Step 4: Document findings**

Create a note of any issues found

---

### Task 19: Test Performance

**Step 1: Run Lighthouse audit**

```bash
npm run build
npm run start
```

Then in Chrome DevTools → Lighthouse → Run audit

**Step 2: Check metrics**

Target scores:
- Performance: >90
- Accessibility: >95
- Best Practices: >90

**Step 3: Monitor FPS**

In Chrome DevTools → Performance:
- Record while scrolling
- Check FPS stays at 60fps

**Step 4: Document results**

---

### Task 20: Final Integration Test

**Step 1: Test full user flow**

1. Load home page
2. See hero animation
3. Scroll down to feed
4. Hover over article cards
5. Click filters
6. Search for articles
7. Click article to open modal

**Step 2: Test responsive**

Test at breakpoints:
- Mobile: 375px
- Tablet: 768px
- Desktop: 1280px
- Large: 1920px

**Step 3: Cross-browser test**

Test in:
- Chrome
- Firefox
- Safari (if available)

**Step 4: Final commit**

```bash
git add .
git commit -m "feat(frontend): complete Phase 1 cyberpunk redesign implementation"
```

---

## Summary

**Completed:**
- ✅ Foundation (Tailwind config, global CSS)
- ✅ Cyberpunk components (5 components)
- ✅ Hero section (3 components)
- ✅ Home page integration
- ✅ Basic accessibility
- ✅ Performance testing

**Next Steps (Not in this plan):**
- Complete article feed redesign
- Add real API data to metrics
- Optimize canvas performance
- Add more micro-interactions
- Build remaining pages with cyberpunk theme

**Total Estimated Time:** 4-6 hours

---

## Troubleshooting

**Issue: TypeScript errors**
- Run: `npx tsc --noEmit`
- Fix type errors before proceeding

**Issue: Animations not working**
- Check Tailwind config was updated
- Verify globals.css has animations
- Clear Next.js cache: `rm -rf .next`

**Issue: Matrix rain performance**
- Reduce particle count
- Lower FPS on mobile
- Add performance monitoring

**Issue: Colors not showing**
- Verify Tailwind config colors
- Check class names match config
- Rebuild: `npm run dev` restart

---

**End of Plan**
