'use client';

import { PowerBIDashboard } from '@/components/analytics/PowerBIDashboard';
import { BarChart3 } from 'lucide-react';

export default function AnalyticsPage() {
  return (
    <main className="min-h-screen bg-anthracite-950 relative z-10">
      <div className="container max-w-7xl py-8">
        <div className="mb-8 p-6 rounded-2xl bg-anthracite-800/50 border border-violet/20">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-8 h-8 text-violet" />
            <h1 className="text-3xl font-bold text-gradient-violet">
              Analytics
            </h1>
          </div>
          <p className="text-muted-foreground ml-11">
            Visualize your trends and watch statistics
          </p>
        </div>

        <PowerBIDashboard />
      </div>
    </main>
  );
}
