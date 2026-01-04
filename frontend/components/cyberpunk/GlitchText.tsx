'use client';

import { cn } from '@/lib/utils';

interface GlitchTextProps {
  children: React.ReactNode;
  className?: string;
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span';
}

/**
 * Text component with cyberpunk glitch animation effect.
 * Uses the .glitch-text CSS class for the animation.
 *
 * @example
 * <GlitchText as="h1" className="text-4xl">
 *   Welcome to ZenWatch
 * </GlitchText>
 */
export const GlitchText = ({
  children,
  className,
  as: Component = 'span'
}: GlitchTextProps) => {
  return (
    <Component className={cn('glitch-text', className)}>
      {children}
    </Component>
  );
};
