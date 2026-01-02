'use client';

import { Card, CardContent } from '@/components/ui/card';
import { BarChart3 } from 'lucide-react';

export const PowerBIDashboard = () => {
  return (
    <Card className="w-full h-full min-h-[600px]">
      <CardContent className="flex flex-col items-center justify-center h-full p-12 text-center">
        <BarChart3 className="w-24 h-24 text-muted-foreground mb-6" />
        <h3 className="text-2xl font-bold mb-2">Power BI Dashboard</h3>
        <p className="text-muted-foreground max-w-md">
          Les dashboards Power BI seront intégrés ici une fois le backend
          configuré avec les embed tokens.
        </p>
        <div className="mt-6 text-xs text-muted-foreground">
          Configuration requise :
          <ul className="list-disc list-inside mt-2 text-left">
            <li>Power BI Workspace ID</li>
            <li>Power BI Report ID</li>
            <li>API endpoint pour embed token</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};
