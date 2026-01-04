'use client';

import { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface MatrixRainProps {
  className?: string;
  color?: string;
  fontSize?: number;
  speed?: number;
}

/**
 * Matrix-style falling characters background effect using Canvas.
 * Creates an animated background of falling green characters.
 * Respects prefers-reduced-motion accessibility setting.
 *
 * @example
 * <MatrixRain className="fixed inset-0 -z-10" color="#00FF41" />
 */
export const MatrixRain = ({
  className,
  color = '#00FF41',
  fontSize = 16,
  speed = 33,
}: MatrixRainProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Characters to use
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
    const columns = Math.floor(canvas.width / fontSize);
    const drops: number[] = Array(columns).fill(1);

    // Animation function
    const draw = () => {
      // Fade effect
      ctx.fillStyle = 'rgba(10, 14, 39, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw characters
      ctx.fillStyle = color;
      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)];
        const x = i * fontSize;
        const y = drops[i] * fontSize;

        ctx.fillText(char, x, y);

        // Reset drop to top randomly
        if (y > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        drops[i]++;
      }
    };

    // Start animation
    const interval = setInterval(draw, speed);

    // Handle resize
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', handleResize);
    };
  }, [color, fontSize, speed]);

  return (
    <canvas
      ref={canvasRef}
      className={cn('pointer-events-none', className)}
      aria-hidden="true"
    />
  );
};
