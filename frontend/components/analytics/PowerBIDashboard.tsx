'use client';

import { Card, CardContent } from '@/components/ui/card';
import { BarChart3, Database, Key, Server } from 'lucide-react';

export const PowerBIDashboard = () => {
  return (
    <Card className="w-full h-full min-h-[600px] bg-black/50 backdrop-blur-sm border-gold-light/30">
      <CardContent className="flex flex-col items-center justify-center h-full p-12 text-center">
        <BarChart3 className="w-24 h-24 text-gold-light/70 mb-6" />
        <h3 className="text-2xl font-bold mb-2 text-gold-light">
          Power BI Dashboard
        </h3>
        <p className="text-gold-light/70 max-w-md mb-8">
          Les dashboards Power BI seront intégrés ici une fois le backend
          configuré avec les embed tokens.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl">
          <div className="bg-black/30 border border-gold-light/20 rounded-lg p-4">
            <Database className="w-8 h-8 text-gold-light/50 mx-auto mb-2" />
            <p className="text-xs text-gold-light/70">Power BI Workspace ID</p>
          </div>
          <div className="bg-black/30 border border-gold-light/20 rounded-lg p-4">
            <Key className="w-8 h-8 text-gold-light/50 mx-auto mb-2" />
            <p className="text-xs text-gold-light/70">Power BI Report ID</p>
          </div>
          <div className="bg-black/30 border border-gold-light/20 rounded-lg p-4">
            <Server className="w-8 h-8 text-gold-light/50 mx-auto mb-2" />
            <p className="text-xs text-gold-light/70">API Embed Token</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
