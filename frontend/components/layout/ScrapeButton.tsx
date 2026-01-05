'use client';

import { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw, Check, AlertCircle } from 'lucide-react';
import { sourcesApi } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface ScrapeButtonProps {
  collapsed?: boolean;
  size?: 'sm' | 'default';
}

type ScrapeStatus = 'idle' | 'scraping' | 'success' | 'error';

export const ScrapeButton = ({ collapsed = false, size = 'sm' }: ScrapeButtonProps) => {
  const [status, setStatus] = useState<ScrapeStatus>('idle');
  const [lastResult, setLastResult] = useState<{ scraped: number; saved: number } | null>(null);
  const { toast } = useToast();

  const pollStatus = useCallback(async (taskId: string) => {
    const maxAttempts = 60; // 2 minutes max
    let attempts = 0;

    const poll = async (): Promise<void> => {
      try {
        const result = await sourcesApi.getScrapingStatus(taskId);

        if (result.status === 'running') {
          attempts++;
          if (attempts < maxAttempts) {
            setTimeout(poll, 2000); // Poll every 2 seconds
          } else {
            setStatus('idle');
            toast({
              title: 'Scraping taking longer than expected',
              description: 'Check back later for results.',
            });
          }
        } else if (result.status === 'success' || result.status === 'partial_success') {
          setStatus('success');
          setLastResult({ scraped: result.articles_scraped, saved: result.articles_saved });
          toast({
            title: 'Scraping complete',
            description: `${result.articles_saved} new articles saved (${result.articles_scraped} scraped)`,
          });
          // Reset to idle after 3 seconds
          setTimeout(() => setStatus('idle'), 3000);
        } else {
          setStatus('error');
          toast({
            title: 'Scraping failed',
            description: result.error_message || 'Unknown error',
            variant: 'destructive',
          });
          setTimeout(() => setStatus('idle'), 3000);
        }
      } catch (error) {
        // Status endpoint might not find the task yet, retry
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000);
        }
      }
    };

    // Start polling after initial delay
    setTimeout(poll, 1000);
  }, [toast]);

  const handleScrape = async () => {
    if (status === 'scraping') return;

    setStatus('scraping');
    try {
      const response = await sourcesApi.triggerScraping();
      toast({
        title: 'Scraping started',
        description: 'Fetching content from all sources...',
      });
      // Start polling for status
      pollStatus(response.task_id);
    } catch (error) {
      console.error('Failed to trigger scraping:', error);
      setStatus('error');
      toast({
        title: 'Scraping failed',
        description: 'Could not start scraping. Please try again.',
        variant: 'destructive',
      });
      setTimeout(() => setStatus('idle'), 3000);
    }
  };

  const getIcon = () => {
    switch (status) {
      case 'scraping':
        return <RefreshCw className="w-4 h-4 animate-spin" />;
      case 'success':
        return <Check className="w-4 h-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <RefreshCw className="w-4 h-4" />;
    }
  };

  const getLabel = () => {
    switch (status) {
      case 'scraping':
        return 'Scraping...';
      case 'success':
        return lastResult ? `+${lastResult.saved}` : 'Done';
      case 'error':
        return 'Error';
      default:
        return 'Scrape';
    }
  };

  return (
    <Button
      variant="ghost"
      size={size}
      onClick={handleScrape}
      disabled={status === 'scraping'}
      className={cn(
        'text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20 transition-all',
        status === 'success' && 'text-green-400 hover:text-green-300',
        status === 'error' && 'text-red-400 hover:text-red-300',
        collapsed && 'mx-auto'
      )}
      title={status === 'scraping' ? 'Scraping in progress...' : 'Trigger scraping'}
    >
      {getIcon()}
      {!collapsed && <span className="ml-2">{getLabel()}</span>}
    </Button>
  );
};
