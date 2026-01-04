'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface ScanLineProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Wrapper component that applies a cyberpunk scanning line effect.
 * Uses the global .scan-line CSS class for animation defined in globals.css.
 *
 * @example
 * <ScanLine className="relative">
 *   <div>Content with scan effect</div>
 * </ScanLine>
 */
export const ScanLine = ({ children, className }: ScanLineProps) => {
  return (
    <div className={cn('scan-line', className)}>
      {children}
    </div>
  );
};
