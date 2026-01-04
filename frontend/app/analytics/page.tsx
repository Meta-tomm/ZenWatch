'use client';

import { PowerBIDashboard } from '@/components/analytics/PowerBIDashboard';
import { CornerBrackets } from '@/components/cyberpunk/CornerBrackets';
import { BarChart3 } from 'lucide-react';

export default function AnalyticsPage() {
  return (
    <main className="min-h-screen bg-charcoal-950 relative z-10">
      <div className="container max-w-7xl py-8">
        <CornerBrackets color="gold-light" className="mb-8 p-6">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-8 h-8 text-gold-light" />
            <h1 className="text-3xl font-bold glow-text text-gold-light">
              Analytics
            </h1>
          </div>
          <p className="text-gold-light/70 ml-11">
            Visualisez vos tendances et statistiques de veille
          </p>
        </CornerBrackets>

        <PowerBIDashboard />
      </div>
    </main>
  );
}
