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
          willChange: 'transform',
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
