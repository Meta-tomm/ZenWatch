"""
Quick test script for the enhanced scraper system

Tests:
1. ScrapedArticle Pydantic validation
2. HackerNews scraper with retry logic
3. Redis caching (if Redis available)
"""

import asyncio
from app.scrapers.registry import ScraperRegistry
from app.schemas.scraped_article import ScrapedArticle


async def test_hackernews_scraper():
    """Test HackerNews scraper"""
    print("=== Testing HackerNews Scraper ===\n")

    # Get scraper from registry
    registry = ScraperRegistry()
    scraper = registry.get('hackernews')

    if not scraper:
        print("ERROR: HackerNews scraper not registered")
        return

    print(f"Scraper: {scraper.display_name} v{scraper.version}")
    print(f"Rate Limit: {scraper.rate_limiter.rate} req/min")
    print(f"Cache TTL: {scraper.CACHE_TTL}s")
    print(f"Max Retries: {scraper.MAX_RETRIES}\n")

    # Test configuration
    config = {
        'max_articles': 5  # Fetch only 5 for quick test
    }

    keywords = ['python', 'rust', 'typescript', 'javascript']

    print(f"Keywords: {keywords}")
    print(f"Max articles: {config['max_articles']}\n")

    # Scrape articles
    print("Scraping...")
    async with scraper:
        try:
            articles = await scraper.scrape(config, keywords)

            print(f"\n✅ Successfully scraped {len(articles)} articles\n")

            # Display results
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article.title}")
                print(f"   URL: {article.url}")
                print(f"   Author: {article.author}")
                print(f"   Score: {article.upvotes} | Comments: {article.comments_count}")
                print(f"   Published: {article.published_at}")
                print(f"   Source: {article.source_type}")
                print()

            # Validate Pydantic models
            print("=== Pydantic Validation ===")
            for article in articles:
                assert isinstance(article, ScrapedArticle), "Not a ScrapedArticle instance"
                assert article.title, "Missing title"
                assert article.url, "Missing URL"
                assert article.source_type == 'hackernews', "Wrong source_type"

            print("✅ All Pydantic validations passed")

        except Exception as e:
            print(f"\n❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()


async def test_caching():
    """Test caching (requires Redis)"""
    print("\n=== Testing Redis Caching ===\n")

    try:
        import redis.asyncio as redis
        redis_client = await redis.from_url("redis://localhost:6379/0")

        registry = ScraperRegistry()
        scraper = registry.get('hackernews')

        # Pass Redis client
        scraper.redis = redis_client

        config = {'max_articles': 3}
        keywords = ['python']

        print("First scrape (cache miss expected)...")
        async with scraper:
            start = asyncio.get_event_loop().time()
            articles1 = await scraper.scrape_with_cache(config, keywords)
            duration1 = asyncio.get_event_loop().time() - start

        print(f"✅ Scraped {len(articles1)} articles in {duration1:.2f}s")

        print("\nSecond scrape (cache hit expected)...")
        async with scraper:
            start = asyncio.get_event_loop().time()
            articles2 = await scraper.scrape_with_cache(config, keywords)
            duration2 = asyncio.get_event_loop().time() - start

        print(f"✅ Retrieved {len(articles2)} articles in {duration2:.2f}s")

        if duration2 < duration1 * 0.1:  # Cache should be 10x faster
            print(f"\n✅ Caching works! Speedup: {duration1/duration2:.1f}x")
        else:
            print(f"\n⚠️  No significant speedup detected (may not be cached)")

        await redis_client.close()

    except Exception as e:
        print(f"⚠️  Caching test skipped: {e}")
        print("(Make sure Redis is running: docker-compose up -d)")


async def test_devto_scraper():
    """Test Dev.to scraper"""
    print("\n=== Testing Dev.to Scraper ===\n")

    # Get scraper from registry
    registry = ScraperRegistry()
    scraper = registry.get('devto')

    if not scraper:
        print("ERROR: Dev.to scraper not registered")
        return

    print(f"Scraper: {scraper.display_name} v{scraper.version}")
    print(f"Rate Limit: {scraper.rate_limiter.rate} req/min")
    print(f"Cache TTL: {scraper.CACHE_TTL}s")
    print(f"Max Retries: {scraper.MAX_RETRIES}\n")

    # Test configuration
    config = {
        'max_articles': 5
    }

    keywords = ['python', 'rust', 'typescript']

    print(f"Keywords (tags): {keywords}")
    print(f"Max articles: {config['max_articles']}\n")

    # Scrape articles
    print("Scraping...")
    async with scraper:
        try:
            articles = await scraper.scrape(config, keywords)

            print(f"\n✅ Successfully scraped {len(articles)} articles\n")

            # Display results
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article.title}")
                print(f"   URL: {article.url}")
                print(f"   Author: {article.author}")
                print(f"   Reactions: {article.upvotes} | Comments: {article.comments_count}")
                print(f"   Published: {article.published_at}")
                print(f"   Tags: {', '.join(article.tags[:5])}")
                print()

            # Validate Pydantic models
            print("=== Pydantic Validation ===")
            for article in articles:
                assert isinstance(article, ScrapedArticle), "Not a ScrapedArticle instance"
                assert article.title, "Missing title"
                assert article.url, "Missing URL"
                assert article.source_type == 'devto', "Wrong source_type"

            print("✅ All Pydantic validations passed")

        except Exception as e:
            print(f"\n❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Run all tests"""
    await test_hackernews_scraper()
    await test_devto_scraper()
    await test_caching()


if __name__ == '__main__':
    asyncio.run(main())
