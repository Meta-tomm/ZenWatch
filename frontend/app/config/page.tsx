import { KeywordManager } from '@/components/config/KeywordManager';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function ConfigPage() {
  return (
    <div className="container max-w-6xl py-6">
      <Tabs defaultValue="keywords" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="keywords">Mots-clés</TabsTrigger>
          <TabsTrigger value="sources">Sources</TabsTrigger>
          <TabsTrigger value="preferences">Préférences</TabsTrigger>
        </TabsList>

        <TabsContent value="keywords">
          <KeywordManager />
        </TabsContent>

        <TabsContent value="sources">
          <div className="text-center text-muted-foreground py-12">
            Sources management coming soon...
          </div>
        </TabsContent>

        <TabsContent value="preferences">
          <div className="text-center text-muted-foreground py-12">
            User preferences coming soon...
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
