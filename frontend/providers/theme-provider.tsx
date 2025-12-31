'use client';

import { useEffect } from 'react';
import { useUIStore } from '@/store/ui-store';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);

  useEffect(() => {
    // Apply theme on mount
    setTheme(theme);
  }, [theme, setTheme]);

  return <>{children}</>;
}
