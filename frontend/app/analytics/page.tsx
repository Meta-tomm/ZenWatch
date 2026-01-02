import { PowerBIDashboard } from '@/components/analytics/PowerBIDashboard';

export default function AnalyticsPage() {
  return (
    <div className="container max-w-7xl py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Analytics</h1>
        <p className="text-muted-foreground">
          Visualisez vos tendances et statistiques de veille
        </p>
      </div>

      <PowerBIDashboard />
    </div>
  );
}
