'use client';

import { PowerBIDashboard } from '@/components/analytics/PowerBIDashboard';
import { MatrixRain } from '@/components/cyberpunk/MatrixRain';
import { CornerBrackets } from '@/components/cyberpunk/CornerBrackets';
import { BarChart3 } from 'lucide-react';

export default function AnalyticsPage() {
  return (
    <>
      <MatrixRain className="fixed inset-0 -z-10" color="#00FF41" speed={33} />

      <main className="min-h-screen relative z-10">
        <div className="container max-w-7xl py-8">
          <CornerBrackets color="yellow" className="mb-8 p-6">
            <div className="flex items-center gap-3 mb-2">
              <BarChart3 className="w-8 h-8 text-cyber-yellow" />
              <h1 className="text-3xl font-bold glow-text text-cyber-yellow">
                Analytics
              </h1>
            </div>
            <p className="text-cyber-yellow/70 ml-11">
              Visualisez vos tendances et statistiques de veille
            </p>
          </CornerBrackets>

          <PowerBIDashboard />
        </div>
      </main>
    </>
  );
}
