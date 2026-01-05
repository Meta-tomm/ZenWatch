'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { sourcesApi } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface ScrapeButtonProps {
  collapsed?: boolean;
  size?: 'sm' | 'default';
}

export const ScrapeButton = ({ collapsed = false, size = 'sm' }: ScrapeButtonProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleScrape = async () => {
    if (isLoading) return;

    setIsLoading(true);
    try {
      await sourcesApi.triggerScraping();
      toast({
        title: 'Scraping started',
        description: 'Fetching new content from all sources...',
      });
    } catch (error) {
      console.error('Failed to trigger scraping:', error);
      toast({
        title: 'Scraping failed',
        description: 'Could not start scraping. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      variant="ghost"
      size={size}
      onClick={handleScrape}
      disabled={isLoading}
      className={cn(
        'text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20',
        collapsed && 'mx-auto'
      )}
      title="Trigger scraping"
    >
      <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
      {!collapsed && <span className="ml-2">Scrape</span>}
    </Button>
  );
};
