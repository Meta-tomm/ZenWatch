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
