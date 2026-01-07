'use client';

import { KeywordManager } from '@/components/config/KeywordManager';
import { AdminGuard } from '@/components/admin/AdminGuard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings, Key, Database, User } from 'lucide-react';

export default function ConfigPage() {
  return (
    <AdminGuard>
    <main className="min-h-screen bg-anthracite-950 relative z-10">
      <div className="container max-w-6xl py-8">
        <div className="mb-8 p-6 rounded-2xl bg-anthracite-800/50 border border-violet/20">
          <div className="flex items-center gap-3 mb-2">
            <Settings className="w-8 h-8 text-violet" />
            <h1 className="text-3xl font-bold text-gradient-violet">
              Configuration
            </h1>
          </div>
          <p className="text-muted-foreground ml-11">
            Customize your tech watch experience
          </p>
        </div>

        <Tabs defaultValue="keywords" className="w-full">
          <TabsList className="mb-6 bg-anthracite-800/50 backdrop-blur-sm border border-violet/20">
            <TabsTrigger
              value="keywords"
              className="data-[state=active]:bg-violet/20 data-[state=active]:text-violet-light"
            >
              <Key className="w-4 h-4 mr-2" />
              Keywords
            </TabsTrigger>
            <TabsTrigger
              value="sources"
              className="data-[state=active]:bg-violet/20 data-[state=active]:text-violet-light"
            >
              <Database className="w-4 h-4 mr-2" />
              Sources
            </TabsTrigger>
            <TabsTrigger
              value="preferences"
              className="data-[state=active]:bg-violet/20 data-[state=active]:text-violet-light"
            >
              <User className="w-4 h-4 mr-2" />
              Preferences
            </TabsTrigger>
          </TabsList>

          <TabsContent value="keywords">
            <KeywordManager />
          </TabsContent>

          <TabsContent value="sources">
            <div className="bg-anthracite-800/50 backdrop-blur-sm border border-violet/20 rounded-lg p-12 text-center">
              <Database className="w-16 h-16 text-violet/50 mx-auto mb-4" />
              <p className="text-muted-foreground">
                Sources management coming soon...
              </p>
            </div>
          </TabsContent>

          <TabsContent value="preferences">
            <div className="bg-anthracite-800/50 backdrop-blur-sm border border-violet/20 rounded-lg p-12 text-center">
              <User className="w-16 h-16 text-violet/50 mx-auto mb-4" />
              <p className="text-muted-foreground">
                User preferences coming soon...
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </main>
    </AdminGuard>
  );
}
