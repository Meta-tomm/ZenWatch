import { HeroSection } from '@/components/home/HeroSection';
import { FilterBar } from '@/components/feed/FilterBar';
import { ArticleFeed } from '@/components/feed/ArticleFeed';
import { ArticleModal } from '@/components/feed/ArticleModal';

export default function Home() {
  return (
    <>
      <main>
        <HeroSection className="min-h-screen" />

        <div className="flex flex-col h-full">
          <FilterBar />
          <ArticleFeed />
        </div>
      </main>
      <ArticleModal />
    </>
  );
}
