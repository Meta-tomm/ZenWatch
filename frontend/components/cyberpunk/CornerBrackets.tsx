'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface CornerBracketsProps {
  children: React.ReactNode;
  className?: string;
  color?: 'blue' | 'yellow' | 'green';
}

/**
 * Adds HUD-style corner brackets around content for cyberpunk aesthetic.
 * Creates decorative corner elements using CSS borders.
 *
 * @example
 * <CornerBrackets color="blue">
 *   <div className="p-4">Content with corner brackets</div>
 * </CornerBrackets>
 */
export const CornerBrackets = ({
  children,
  className,
  color = 'blue'
}: CornerBracketsProps) => {
  const colorMap = {
    blue: 'border-cyber-blue',
    yellow: 'border-cyber-yellow',
    green: 'border-cyber-green',
  };

  return (
    <div className={cn('relative', className)}>
      {/* Top-left bracket */}
      <div className={cn(
        'absolute top-0 left-0 w-4 h-4',
        'border-l-2 border-t-2',
        colorMap[color]
      )} />

      {/* Top-right bracket */}
      <div className={cn(
        'absolute top-0 right-0 w-4 h-4',
        'border-r-2 border-t-2',
        colorMap[color]
      )} />

      {/* Bottom-left bracket */}
      <div className={cn(
        'absolute bottom-0 left-0 w-4 h-4',
        'border-l-2 border-b-2',
        colorMap[color]
      )} />

      {/* Bottom-right bracket */}
      <div className={cn(
        'absolute bottom-0 right-0 w-4 h-4',
        'border-r-2 border-b-2',
        colorMap[color]
      )} />

      {children}
    </div>
  );
};
