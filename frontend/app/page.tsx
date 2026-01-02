import { FilterBar } from '@/components/feed/FilterBar';
import { ArticleFeed } from '@/components/feed/ArticleFeed';
import { ArticleModal } from '@/components/feed/ArticleModal';

export default function Home() {
  return (
    <>
      <div className="flex flex-col h-full">
        <FilterBar />
        <ArticleFeed />
      </div>
      <ArticleModal />
    </>
  );
}
