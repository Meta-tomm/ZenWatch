'use client';

import { PowerBIDashboard } from '@/components/analytics/PowerBIDashboard';
import { AnalyticsStats } from '@/components/analytics/AnalyticsStats';
import { BarChart3, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function AnalyticsPage() {
  return (
    <main className="min-h-screen bg-anthracite-950 relative z-10">
      {/* Header */}
      <div className="sticky top-0 z-40 border-b border-violet-500/20 bg-anthracite-900/95 backdrop-blur supports-[backdrop-filter]:bg-anthracite-900/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="sm" className="gap-2 text-violet-300 hover:text-violet-200 hover:bg-violet-500/20">
                <ArrowLeft className="w-4 h-4" />
                Accueil
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <BarChart3 className="w-6 h-6 text-violet-400" />
              <h1 className="text-2xl font-bold text-gradient-violet">
                Analytics
              </h1>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Stats */}
      <AnalyticsStats />

      {/* Power BI Dashboard */}
      <div className="container max-w-7xl py-8">
        <PowerBIDashboard />
      </div>
    </main>
  );
}
