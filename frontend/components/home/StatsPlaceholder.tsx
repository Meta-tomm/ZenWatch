'use client';

import { BarChart3, TrendingUp, Target } from 'lucide-react';
import { CornerBrackets } from '@/components/cyberpunk';

export const StatsPlaceholder = () => {
  return (
    <div className="w-full">
      <CornerBrackets color="gold-dark">
        <div className="bg-charcoal-900/50 border border-gold-dark/30 p-8">
          <div className="flex flex-col items-center justify-center min-h-[300px] space-y-6">
            <div className="flex items-center gap-4">
              <BarChart3 className="w-12 h-12 text-gold-dark animate-pulse" />
              <TrendingUp className="w-12 h-12 text-gold-dark animate-pulse delay-100" />
              <Target className="w-12 h-12 text-gold-dark animate-pulse delay-200" />
            </div>

            <div className="text-center space-y-2">
              <h3 className="text-2xl font-bold text-gold-dark glow-text">
                Analytics Dashboard
              </h3>
              <p className="text-muted-foreground max-w-md">
                Power BI integration coming soon. Track trends, analyze patterns, and discover insights from your tech feed.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4 w-full max-w-2xl mt-4">
              <div className="bg-charcoal-800/70 border border-gold/30 p-4 rounded text-center">
                <div className="text-3xl font-bold text-gold-dark">-</div>
                <div className="text-xs text-muted-foreground mt-1">Articles Analyzed</div>
              </div>
              <div className="bg-charcoal-800/70 border border-gold/30 p-4 rounded text-center">
                <div className="text-3xl font-bold text-gold-dark">-</div>
                <div className="text-xs text-muted-foreground mt-1">Trending Topics</div>
              </div>
              <div className="bg-charcoal-800/70 border border-gold/30 p-4 rounded text-center">
                <div className="text-3xl font-bold text-gold-dark">-</div>
                <div className="text-xs text-muted-foreground mt-1">Top Sources</div>
              </div>
            </div>
          </div>
        </div>
      </CornerBrackets>
    </div>
  );
};
