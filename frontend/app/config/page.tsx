'use client';

import { KeywordManager } from '@/components/config/KeywordManager';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { MatrixRain } from '@/components/cyberpunk/MatrixRain';
import { CornerBrackets } from '@/components/cyberpunk/CornerBrackets';
import { Settings, Key, Database, User } from 'lucide-react';

export default function ConfigPage() {
  return (
    <>
      <MatrixRain className="fixed inset-0 -z-10" color="#00FF41" speed={33} />

      <main className="min-h-screen relative z-10">
        <div className="container max-w-6xl py-8">
          <CornerBrackets color="blue" className="mb-8 p-6">
            <div className="flex items-center gap-3 mb-2">
              <Settings className="w-8 h-8 text-cyber-blue" />
              <h1 className="text-3xl font-bold glow-text text-cyber-blue">
                Configuration
              </h1>
            </div>
            <p className="text-cyber-blue/70 ml-11">
              Personnalisez votre expérience de veille technologique
            </p>
          </CornerBrackets>

          <Tabs defaultValue="keywords" className="w-full">
            <TabsList className="mb-6 bg-cyber-black/50 backdrop-blur-sm border border-cyber-blue/30">
              <TabsTrigger
                value="keywords"
                className="data-[state=active]:bg-cyber-blue/20 data-[state=active]:text-cyber-blue"
              >
                <Key className="w-4 h-4 mr-2" />
                Mots-clés
              </TabsTrigger>
              <TabsTrigger
                value="sources"
                className="data-[state=active]:bg-cyber-blue/20 data-[state=active]:text-cyber-blue"
              >
                <Database className="w-4 h-4 mr-2" />
                Sources
              </TabsTrigger>
              <TabsTrigger
                value="preferences"
                className="data-[state=active]:bg-cyber-blue/20 data-[state=active]:text-cyber-blue"
              >
                <User className="w-4 h-4 mr-2" />
                Préférences
              </TabsTrigger>
            </TabsList>

            <TabsContent value="keywords">
              <KeywordManager />
            </TabsContent>

            <TabsContent value="sources">
              <div className="bg-cyber-black/50 backdrop-blur-sm border border-cyber-blue/30 rounded-lg p-12 text-center">
                <Database className="w-16 h-16 text-cyber-blue/50 mx-auto mb-4" />
                <p className="text-cyber-blue/70">
                  Sources management coming soon...
                </p>
              </div>
            </TabsContent>

            <TabsContent value="preferences">
              <div className="bg-cyber-black/50 backdrop-blur-sm border border-cyber-blue/30 rounded-lg p-12 text-center">
                <User className="w-16 h-16 text-cyber-blue/50 mx-auto mb-4" />
                <p className="text-cyber-blue/70">
                  User preferences coming soon...
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </>
  );
}
