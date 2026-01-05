'use client';

import { ThemeToggle } from '@/components/ThemeToggle';
import { Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const TopBar = () => {
  return (
    <header className="md:hidden sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <div className="flex items-center justify-between h-14 px-4">
        <h1 className="text-lg font-bold text-gradient-violet">
          ZenWatch
        </h1>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <Search className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Filter className="w-4 h-4" />
          </Button>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};
