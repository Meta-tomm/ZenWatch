'use client';

import { Button } from '@/components/ui/button';
import { LayoutGrid, List } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { LibraryFilter, LibraryView } from '@/types';

interface LibraryFiltersProps {
  filter: LibraryFilter;
  view: LibraryView;
  unreadOnly: boolean;
  onFilterChange: (filter: LibraryFilter) => void;
  onViewChange: (view: LibraryView) => void;
  onUnreadOnlyChange: (unreadOnly: boolean) => void;
}

const filters: { value: LibraryFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'articles', label: 'Articles' },
  { value: 'videos', label: 'Videos' },
];

export const LibraryFilters = ({
  filter,
  view,
  unreadOnly,
  onFilterChange,
  onViewChange,
  onUnreadOnlyChange,
}: LibraryFiltersProps) => {
  return (
    <div className="flex items-center justify-between gap-4 flex-wrap">
      {/* Type filters */}
      <div className="flex items-center gap-2">
        {filters.map((f) => (
          <Button
            key={f.value}
            variant={filter === f.value ? 'default' : 'ghost'}
            size="sm"
            onClick={() => onFilterChange(f.value)}
            className={cn(
              filter === f.value
                ? 'bg-violet-600 hover:bg-violet-700 text-white'
                : 'text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20'
            )}
          >
            {f.label}
          </Button>
        ))}

        <div className="w-px h-6 bg-violet-500/30 mx-2" />

        <Button
          variant={unreadOnly ? 'default' : 'ghost'}
          size="sm"
          onClick={() => onUnreadOnlyChange(!unreadOnly)}
          className={cn(
            unreadOnly
              ? 'bg-violet-600 hover:bg-violet-700 text-white'
              : 'text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20'
          )}
        >
          Unread
        </Button>
      </div>

      {/* View toggle */}
      <div className="flex items-center gap-1 bg-anthracite-800 rounded-lg p-1">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onViewChange('list')}
          className={cn(
            'px-2',
            view === 'list'
              ? 'bg-violet-600 text-white hover:bg-violet-700'
              : 'text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20'
          )}
        >
          <List className="w-4 h-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onViewChange('grid')}
          className={cn(
            'px-2',
            view === 'grid'
              ? 'bg-violet-600 text-white hover:bg-violet-700'
              : 'text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20'
          )}
        >
          <LayoutGrid className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};
