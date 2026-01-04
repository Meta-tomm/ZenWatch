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
    <div className="sticky top-0 z-30 bg-charcoal-900/50 backdrop-blur-sm border-b border-gold/30 p-4">
      {/* Search */}
      <div className="flex items-center gap-2 mb-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gold/70" />
          <Input
            placeholder="Rechercher..."
            value={activeFilters.search}
            onChange={(e) => setFilters({ search: e.target.value })}
            className="pl-9 bg-charcoal-800/70 border-gold/50 text-gold placeholder:text-gold/50 focus:border-gold focus:ring-gold/30"
          />
        </div>

        {/* Sort */}
        <Select
          value={activeFilters.sort}
          onValueChange={(value) =>
            setFilters({ sort: value as 'score' | 'date' | 'popularity' })
          }
        >
          <SelectTrigger className="w-32 bg-charcoal-800/70 border-gold/50 text-gold focus:border-gold focus:ring-gold/30">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-charcoal-900/95 border-gold/50">
            <SelectItem value="score" className="text-gold hover:bg-gold/20 focus:bg-gold/20">Score</SelectItem>
            <SelectItem value="date" className="text-gold hover:bg-gold/20 focus:bg-gold/20">Date</SelectItem>
            <SelectItem value="popularity" className="text-gold hover:bg-gold/20 focus:bg-gold/20">Popularité</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Category Pills */}
      <div className="space-y-2">
        <div className="text-xs text-gold/70 font-medium">Catégories</div>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => {
            const isActive = activeFilters.categories.includes(cat);
            return (
              <Badge
                key={cat}
                variant={isActive ? 'default' : 'outline'}
                className={`cursor-pointer transition-all ${
                  isActive
                    ? 'bg-gold/30 text-gold border-gold/70 shadow-[0_0_10px_rgba(0,255,255,0.3)]'
                    : 'bg-charcoal-800/50 text-gold/70 border-gold/30 hover:bg-gold/10 hover:border-gold/50'
                }`}
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
        <div className="text-xs text-gold/70 font-medium">Sources</div>
        <div className="flex flex-wrap gap-2">
          {SOURCES.map((source) => {
            const isActive = activeFilters.sources.includes(source.id);
            return (
              <Badge
                key={source.id}
                variant={isActive ? 'default' : 'outline'}
                className={`cursor-pointer transition-all ${
                  isActive
                    ? 'bg-gold/30 text-gold border-gold/70 shadow-[0_0_10px_rgba(0,255,255,0.3)]'
                    : 'bg-charcoal-800/50 text-gold/70 border-gold/30 hover:bg-gold/10 hover:border-gold/50'
                }`}
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
        <div className="flex items-center gap-2 pt-2 mt-3 border-t border-gold/30">
          <span className="text-sm text-gold/70">Filtres actifs:</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="h-7 bg-charcoal-800/50 text-gold border border-gold/30 hover:bg-gold/20 hover:border-gold/50"
          >
            <X className="w-3 h-3 mr-1" />
            Effacer
          </Button>
        </div>
      )}
    </div>
  );
};
