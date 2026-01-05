# Frontend 3D Theme Redesign - Design Document

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Date**: 2026-01-04
**Goal**: Transform ZenWatch frontend into a premium 3D experience with violet/magenta gradients - impressive home page with 3D animations, minimal articles/config pages

---

## Design Vision

### Two-Tier Experience

**Home Page (/)**: Immersive 3D experience
- 3D card animations (Apple-style lift & rotate)
- Parallax background layers
- Premium violet/magenta gradients
- Impressive "wow" factor for featured content

**Articles/Config Pages**: Clean, minimal, content-focused
- Subtle fade-in transitions only
- No heavy 3D effects
- Fast, fluid navigation
- Focus on readability and usability

---

## Color Palette

### Background Layers
```css
--bg-deepest: #0D0D0D        /* Almost pure black */
--bg-dark: #1A1A1D           /* Cold charcoal */
--bg-panel: #25252A          /* Anthracite gray */
--bg-elevated: #2D2D32       /* Elevated surfaces */
```

### Accent Colors
```css
--violet-primary: #8B5CF6    /* Purple-500 */
--magenta-primary: #D946EF   /* Fuchsia-500 */
--violet-light: #A78BFA      /* Purple-400 */
--violet-dark: #7C3AED       /* Purple-600 */
```

### Gradients
```css
--gradient-primary: linear-gradient(135deg, #8B5CF6 0%, #D946EF 100%)
--gradient-subtle: linear-gradient(180deg, rgba(139, 92, 246, 0.1) 0%, rgba(217, 70, 239, 0.05) 100%)
--gradient-glow: radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.3), transparent 70%)
```

### Text Colors
```css
--text-primary: #F5F5F7      /* Almost white */
--text-secondary: #A1A1AA    /* Gray-400 */
--text-muted: #71717A        /* Gray-500 */
```

---

## Home Page Design

### Layout Structure
```
┌────────────────────────────────────────────────────────┐
│  Navigation (minimal, transparent)                     │
└────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  ZENWATCH                                        │ │
│  │  [Large title with violet gradient glow]        │ │
│  │  Votre veille tech intelligente                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────┐    ┌──────────────────┐        │
│  │  Best Article    │    │  Best Video      │        │
│  │  of the Week     │    │  of the Week     │        │
│  │                  │    │                  │        │
│  │  [3D Card]       │    │  [3D Card]       │        │
│  │  • Lift on hover │    │  • Lift on hover │        │
│  │  • Rotate subtle │    │  • Rotate subtle │        │
│  │  • Glow effect   │    │  • Glow effect   │        │
│  └──────────────────┘    └──────────────────┘        │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Stats Dashboard Preview                        │ │
│  │  (Power BI Placeholder)                         │ │
│  │  [Parallax background - grid pattern]           │ │
│  │  [Gradient overlay]                             │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 3D Card Animation Specs

**Transform Properties**:
```css
/* Resting state */
transform: perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px);
transition: transform 0.6s cubic-bezier(0.23, 1, 0.32, 1);

/* Hover state */
transform: perspective(1000px) rotateX(-5deg) rotateY(5deg) translateZ(20px);
box-shadow:
  0 20px 60px -15px rgba(139, 92, 246, 0.5),
  0 0 40px rgba(217, 70, 239, 0.3);
```

**Scroll-based Animation**:
- Cards fade in from bottom with slight rotation
- Parallax effect on background grid (moves slower than scroll)
- Glow intensifies as cards enter viewport

### Parallax Background

**Layers** (back to front):
1. Deep gradient background (static)
2. Animated grid pattern (slow parallax, -0.3 scroll speed)
3. Floating particles/dots (medium parallax, -0.5 scroll speed)
4. Content layer (normal scroll speed)

**Grid Pattern**:
```
Isometric grid with violet/magenta glow lines
Opacity: 0.1 - 0.2
Animation: Subtle fade pulse (3s ease-in-out infinite)
```

---

## Articles Page Design

### Principles
- Clean, minimal, fast
- No 3D transforms
- Focus on content readability
- Smooth scrolling

### Card Design
```
┌─────────────────────────────────────────────┐
│  Title (text-primary, bold)                 │
│  Source • Time • Read time                  │
│                                             │
│  [Category badge] [Tags...]                │
│                                             │
│  Summary preview...                         │
│                                             │
│  ├─ Like/Dislike  ├─ Favorite  ├─ Link    │
└─────────────────────────────────────────────┘

Hover:
- Border glow (violet subtle)
- Background lighten slightly
- NO 3D transform
```

### Animations
- Fade-in on scroll (opacity 0 → 1, 300ms)
- Smooth hover transitions (150ms)
- Filter bar sticky with backdrop blur

---

## Technical Implementation

### Libraries/Tech Stack

**3D & Scroll Animations**:
- `framer-motion` (already installed) - scroll-based animations
- CSS `transform: perspective()` for 3D effects
- `react-intersection-observer` for viewport detection

**Performance**:
- `will-change: transform` on animated elements
- GPU acceleration with `translateZ(0)`
- Lazy load heavy components
- Debounced scroll listeners

### File Structure
```
frontend/
├── components/
│   ├── home/
│   │   ├── Hero3D.tsx              # Main hero with title
│   │   ├── BestArticleCard3D.tsx   # 3D card for best article
│   │   ├── BestVideoCard3D.tsx     # 3D card for best video
│   │   ├── StatsPreview3D.tsx      # Stats with parallax
│   │   └── ParallaxGrid.tsx        # Background grid layer
│   ├── feed/
│   │   ├── ArticleCard.tsx         # Minimal card (UPDATE)
│   │   └── FilterBar.tsx           # Sticky filter (UPDATE)
│   └── ui/
│       └── gradient-border.tsx     # Reusable gradient border
├── lib/
│   ├── animations-3d.ts            # 3D animation variants
│   └── scroll-parallax.ts          # Parallax scroll hook
├── app/
│   ├── page.tsx                    # Home with 3D (REWRITE)
│   ├── articles/page.tsx           # Minimal articles (UPDATE)
│   └── globals.css                 # Update palette (UPDATE)
└── tailwind.config.ts              # New colors (UPDATE)
```

---

## Animation Performance Budget

### Home Page
- Initial paint: < 1.5s
- 3D transforms: 60fps (GPU accelerated)
- Parallax smooth at: 60fps
- Bundle size impact: < +50KB

### Articles Page
- Initial paint: < 1s
- Scroll smoothness: 60fps
- No layout shifts
- Fast navigation

---

## Accessibility

### Motion Preferences
```css
@media (prefers-reduced-motion: reduce) {
  /* Disable 3D transforms */
  .card-3d {
    transform: none !important;
  }

  /* Disable parallax */
  .parallax-layer {
    transform: none !important;
  }

  /* Keep fade-in only */
  .fade-in {
    animation: fade-in 0.01ms !important;
  }
}
```

### Contrast Ratios
- Text on dark bg: > 7:1 (AAA)
- Violet on dark: > 4.5:1 (AA)
- Interactive elements: Clear focus states

---

## Implementation Phases

### Phase 1: Color System (30 min)
- Update `tailwind.config.ts` with new palette
- Update `globals.css` with CSS variables
- Create gradient utilities

### Phase 2: Home Page 3D Components (2h)
- `Hero3D.tsx` with gradient title
- `BestArticleCard3D.tsx` with lift/rotate
- `BestVideoCard3D.tsx` with lift/rotate
- `ParallaxGrid.tsx` background
- `StatsPreview3D.tsx` placeholder

### Phase 3: Articles Page Minimal Update (1h)
- Simplify `ArticleCard.tsx` (remove heavy effects)
- Update `FilterBar.tsx` styling
- Ensure smooth scroll

### Phase 4: Polish & Performance (30 min)
- Test animations on different devices
- Optimize bundle size
- Add `will-change` hints
- Test reduced motion

---

## Visual References

### Inspiration
- **Apple.com product pages**: Card lift animations
- **Stripe.com**: Gradient usage and subtlety
- **Linear.app**: Minimal UI with premium feel
- **Vercel.com**: Parallax backgrounds

### Key Differences
- More aggressive 3D on home (not just hover)
- Violet/magenta vs blue gradients
- Stronger parallax effect
- Dual-tier experience (3D home, minimal articles)

---

## Success Metrics

**Home Page**:
- Users spend >10s on home (engaging)
- 60fps animations verified
- "Wow" feedback from users

**Articles Page**:
- Fast scroll (no jank)
- Easy to read 20+ articles
- Users navigate confidently

**Overall**:
- Lighthouse score > 90
- No layout shifts (CLS = 0)
- Works on mobile smoothly
