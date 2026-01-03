'use client';

import { useUIStore } from '@/store/ui-store';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Search, X } from 'lucide-react';

const CATEGORIES = [
  'healthtech',
  'blockchain',
  'dev',
  'ai',
  'cloud',
  'security',
];

const SOURCES = [
  { id: 'hackernews', name: 'HackerNews' },
  { id: 'devto', name: 'Dev.to' },
  { id: 'reddit', name: 'Reddit' },
];

export const FilterBar = () => {
  const { activeFilters, setFilters, clearFilters } = useUIStore();

  return (
    <div className="sticky top-0 z-30 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b p-4">
      {/* Search */}
      <div className="flex items-center gap-2 mb-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher..."
            value={activeFilters.search}
            onChange={(e) => setFilters({ search: e.target.value })}
            className="pl-9"
          />
        </div>

        {/* Sort */}
        <Select
          value={activeFilters.sort}
          onValueChange={(value) =>
            setFilters({ sort: value as 'score' | 'date' | 'popularity' })
          }
        >
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="score">Score</SelectItem>
            <SelectItem value="date">Date</SelectItem>
            <SelectItem value="popularity">Popularité</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Category Pills */}
      <div className="space-y-2">
        <div className="text-xs text-muted-foreground font-medium">Catégories</div>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => {
            const isActive = activeFilters.categories.includes(cat);
            return (
              <Badge
                key={cat}
                variant={isActive ? 'default' : 'outline'}
                className="cursor-pointer hover:bg-primary/10"
                onClick={() => {
                  const newCategories = isActive
                    ? activeFilters.categories.filter((c) => c !== cat)
                    : [...activeFilters.categories, cat];
                  setFilters({ categories: newCategories });
                }}
              >
                {cat}
              </Badge>
            );
          })}
        </div>
      </div>

      {/* Source Pills */}
      <div className="space-y-2 mt-3">
        <div className="text-xs text-muted-foreground font-medium">Sources</div>
        <div className="flex flex-wrap gap-2">
          {SOURCES.map((source) => {
            const isActive = activeFilters.sources.includes(source.id);
            return (
              <Badge
                key={source.id}
                variant={isActive ? 'default' : 'outline'}
                className="cursor-pointer hover:bg-primary/10"
                onClick={() => {
                  const newSources = isActive
                    ? activeFilters.sources.filter((s) => s !== source.id)
                    : [...activeFilters.sources, source.id];
                  setFilters({ sources: newSources });
                }}
              >
                {source.name}
              </Badge>
            );
          })}
        </div>
      </div>

      {/* Active Filters */}
      {(activeFilters.search ||
        activeFilters.categories.length > 0 ||
        activeFilters.sources.length > 0) && (
        <div className="flex items-center gap-2 pt-2 border-t">
          <span className="text-sm text-muted-foreground">Filtres actifs:</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="h-7"
          >
            <X className="w-3 h-3 mr-1" />
            Effacer
          </Button>
        </div>
      )}
    </div>
  );
};
