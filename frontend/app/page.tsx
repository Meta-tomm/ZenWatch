import { BestArticleCard } from '@/components/home/BestArticleCard';
import { BestVideoCard } from '@/components/home/BestVideoCard';
import { StatsPlaceholder } from '@/components/home/StatsPlaceholder';
import { AnimatedTitle } from '@/components/home/AnimatedTitle';

export default function Home() {
  return (
    <main className="min-h-screen bg-charcoal-950">
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Title */}
        <div className="text-center mb-12">
          <AnimatedTitle
            title="ZENWATCH"
            subtitle="Your intelligent tech watch platform"
          />
        </div>

        {/* Best of the Week Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <BestArticleCard />
          <BestVideoCard />
        </div>

        {/* Stats Placeholder */}
        <div className="mt-12">
          <StatsPlaceholder />
        </div>
      </div>
    </main>
  );
}
