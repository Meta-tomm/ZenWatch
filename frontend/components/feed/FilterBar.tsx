'use client';

import { useEffect, useState } from 'react';
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
import { Checkbox } from '@/components/ui/checkbox';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Search, X, ChevronDown } from 'lucide-react';

const SOURCES = [
  { id: 'arxiv', name: 'arXiv' },
  { id: 'devto', name: 'Dev.to' },
  { id: 'hackernews', name: 'HackerNews' },
  { id: 'official_blogs', name: 'Official Blogs' },
  { id: 'youtube_rss', name: 'YouTube' },
];

const TIME_RANGES = [
  { value: 'all', label: 'All' },
  { value: '24h', label: '24h' },
  { value: '7d', label: '7d' },
  { value: '30d', label: '30d' },
] as const;

export const FilterBar = () => {
  const { activeFilters, setFilters, clearFilters } = useUIStore();
  const [categories, setCategories] = useState<string[]>([]);
  const [isLoadingCategories, setIsLoadingCategories] = useState(true);

  // Fetch categories from API
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/articles/categories/list`
        );
        const data = await response.json();
        setCategories(data.categories || []);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
        setCategories(['ai', 'backend', 'dev', 'frontend', 'models', 'other']);
      } finally {
        setIsLoadingCategories(false);
      }
    };
    fetchCategories();
  }, []);

  const toggleCategory = (cat: string) => {
    const newCategories = activeFilters.categories.includes(cat)
      ? activeFilters.categories.filter((c) => c !== cat)
      : [...activeFilters.categories, cat];
    setFilters({ categories: newCategories });
  };

  const toggleSource = (sourceId: string) => {
    const newSources = activeFilters.sources.includes(sourceId)
      ? activeFilters.sources.filter((s) => s !== sourceId)
      : [...activeFilters.sources, sourceId];
    setFilters({ sources: newSources });
  };

  const getSelectedLabel = (selected: string[], items: { id: string; name: string }[] | string[]) => {
    if (selected.length === 0) return 'All';
    if (selected.length === 1) {
      const item = typeof items[0] === 'string'
        ? selected[0]
        : (items as { id: string; name: string }[]).find(i => i.id === selected[0])?.name || selected[0];
      return item;
    }
    return `${selected.length} selected`;
  };

  const hasActiveFilters =
    activeFilters.search ||
    activeFilters.categories.length > 0 ||
    activeFilters.sources.length > 0 ||
    activeFilters.timeRange !== 'all';

  return (
    <div className="sticky top-0 z-30 bg-anthracite-900/95 backdrop-blur-sm border-b border-violet-500/20 p-3">
      {/* Main filter row */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-violet-400/70" />
          <Input
            placeholder="Search..."
            value={activeFilters.search}
            onChange={(e) => setFilters({ search: e.target.value })}
            className="pl-9 h-9 bg-anthracite-800/70 border-violet-500/30 text-violet-100 placeholder:text-violet-400/50 focus:border-violet-400 focus:ring-violet-400/30"
          />
        </div>

        {/* Categories Dropdown */}
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className="h-9 min-w-[120px] justify-between bg-anthracite-800/70 border-violet-500/30 text-violet-100 hover:bg-violet-500/20 hover:border-violet-400/50"
            >
              <span className="truncate">
                {activeFilters.categories.length > 0
                  ? getSelectedLabel(activeFilters.categories, categories)
                  : 'Categories'}
              </span>
              <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-48 p-2 bg-anthracite-900/95 border-violet-500/30" align="start">
            <div className="space-y-1 max-h-[300px] overflow-y-auto">
              {isLoadingCategories ? (
                <div className="text-sm text-violet-400/70 p-2">Loading...</div>
              ) : (
                categories.map((cat) => (
                  <div
                    key={cat}
                    className="flex items-center space-x-2 p-2 rounded hover:bg-violet-500/20 cursor-pointer"
                    onClick={() => toggleCategory(cat)}
                  >
                    <Checkbox
                      checked={activeFilters.categories.includes(cat)}
                      className="border-violet-500/50 data-[state=checked]:bg-violet-500 data-[state=checked]:border-violet-500"
                    />
                    <span className="text-sm text-violet-100 capitalize">{cat}</span>
                  </div>
                ))
              )}
            </div>
          </PopoverContent>
        </Popover>

        {/* Sources Dropdown */}
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className="h-9 min-w-[120px] justify-between bg-anthracite-800/70 border-violet-500/30 text-violet-100 hover:bg-violet-500/20 hover:border-violet-400/50"
            >
              <span className="truncate">
                {activeFilters.sources.length > 0
                  ? getSelectedLabel(activeFilters.sources, SOURCES)
                  : 'Sources'}
              </span>
              <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-48 p-2 bg-anthracite-900/95 border-violet-500/30" align="start">
            <div className="space-y-1">
              {SOURCES.map((source) => (
                <div
                  key={source.id}
                  className="flex items-center space-x-2 p-2 rounded hover:bg-violet-500/20 cursor-pointer"
                  onClick={() => toggleSource(source.id)}
                >
                  <Checkbox
                    checked={activeFilters.sources.includes(source.id)}
                    className="border-violet-500/50 data-[state=checked]:bg-violet-500 data-[state=checked]:border-violet-500"
                  />
                  <span className="text-sm text-violet-100">{source.name}</span>
                </div>
              ))}
            </div>
          </PopoverContent>
        </Popover>

        {/* Sort Dropdown */}
        <Select
          value={activeFilters.sort}
          onValueChange={(value) =>
            setFilters({ sort: value as 'score' | 'date' | 'popularity' })
          }
        >
          <SelectTrigger className="w-28 h-9 bg-anthracite-800/70 border-violet-500/30 text-violet-100 focus:border-violet-400 focus:ring-violet-400/30">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-anthracite-900/95 border-violet-500/30">
            <SelectItem value="score" className="text-violet-100 hover:bg-violet-500/20 focus:bg-violet-500/20">Score</SelectItem>
            <SelectItem value="date" className="text-violet-100 hover:bg-violet-500/20 focus:bg-violet-500/20">Date</SelectItem>
            <SelectItem value="popularity" className="text-violet-100 hover:bg-violet-500/20 focus:bg-violet-500/20">Popular</SelectItem>
          </SelectContent>
        </Select>

        {/* Time Range Buttons */}
        <div className="flex items-center bg-anthracite-800/70 rounded-md border border-violet-500/30 p-0.5">
          {TIME_RANGES.map((range) => (
            <button
              key={range.value}
              onClick={() => setFilters({ timeRange: range.value })}
              className={`px-3 py-1.5 text-sm rounded transition-all ${
                activeFilters.timeRange === range.value
                  ? 'bg-violet-500/40 text-violet-100 font-medium'
                  : 'text-violet-300/70 hover:text-violet-100 hover:bg-violet-500/20'
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>

        {/* Clear button */}
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="h-9 px-3 text-violet-300/70 hover:text-violet-100 hover:bg-violet-500/20"
          >
            <X className="w-4 h-4 mr-1" />
            Clear
          </Button>
        )}
      </div>

      {/* Active filters badges */}
      {hasActiveFilters && (
        <div className="flex items-center gap-2 mt-2 flex-wrap">
          <span className="text-xs text-violet-400/70">Active:</span>

          {activeFilters.categories.map((cat) => (
            <Badge
              key={cat}
              variant="secondary"
              className="bg-violet-500/20 text-violet-100 border-violet-400/50 cursor-pointer hover:bg-violet-500/30"
              onClick={() => toggleCategory(cat)}
            >
              {cat}
              <X className="w-3 h-3 ml-1" />
            </Badge>
          ))}

          {activeFilters.sources.map((sourceId) => (
            <Badge
              key={sourceId}
              variant="secondary"
              className="bg-emerald-500/20 text-emerald-100 border-emerald-400/50 cursor-pointer hover:bg-emerald-500/30"
              onClick={() => toggleSource(sourceId)}
            >
              {SOURCES.find(s => s.id === sourceId)?.name || sourceId}
              <X className="w-3 h-3 ml-1" />
            </Badge>
          ))}

          {activeFilters.timeRange !== 'all' && (
            <Badge
              variant="secondary"
              className="bg-amber-500/20 text-amber-100 border-amber-400/50 cursor-pointer hover:bg-amber-500/30"
              onClick={() => setFilters({ timeRange: 'all' })}
            >
              {activeFilters.timeRange}
              <X className="w-3 h-3 ml-1" />
            </Badge>
          )}
        </div>
      )}
    </div>
  );
};
