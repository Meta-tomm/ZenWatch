"""
Test Celery scraping task

Tests the complete scraping flow:
1. Trigger scrape_all_sources task
2. Check task status
3. Verify articles were saved to database
"""

import asyncio
from app.tasks.scraping import scrape_all_sources_async
from app.database import SessionLocal
from app.models.article import Article
from app.models.source import Source
from app.models.keyword import Keyword


async def test_scraping_task():
    """Test the scraping task directly (without Celery)"""
    print("=== Testing Scraping Task (Direct Call) ===\n")

    db = SessionLocal()

    try:
        # Check database state before
        sources_count = db.query(Source).filter_by(is_active=True).count()
        keywords_count = db.query(Keyword).filter_by(is_active=True).count()
        articles_before = db.query(Article).count()

        print(f"Database state BEFORE scraping:")
        print(f"- Active sources: {sources_count}")
        print(f"- Active keywords: {keywords_count}")
        print(f"- Total articles in DB: {articles_before}\n")

        if sources_count == 0:
            print("⚠️  No active sources found in database!")
            print("Run: poetry run python -m app.scripts.seed_sources")
            return

        if keywords_count == 0:
            print("⚠️  No active keywords found in database!")
            print("Using default keywords instead")

        # Run scraping task
        print("Starting scraping task...\n")
        result = await scrape_all_sources_async(
            db=db,
            keywords=None,  # Will fetch from DB or use defaults
            task_id="test-manual"
        )

        print("\n=== Scraping Task Results ===\n")
        print(f"Status: {result['status']}")
        print(f"Sources total: {result['sources_total']}")
        print(f"Sources scraped: {result['sources_scraped']}")
        print(f"Articles scraped: {result['articles_scraped']}")
        print(f"Articles saved: {result['articles_saved']}")
        print(f"Duplicates skipped: {result['duplicates']}")
        print(f"Errors: {result['errors']}")
        print(f"Keywords used: {result['keywords_used']}\n")

        # Show per-source results
        print("=== Per-Source Results ===\n")
        for source_result in result['results']:
            status_icon = "✅" if source_result['status'] == 'success' else "❌"
            print(f"{status_icon} {source_result['source']}: {source_result['status']}")

            if source_result['status'] == 'success':
                print(f"   Scraped: {source_result['articles_scraped']}")
                print(f"   Saved: {source_result['articles_saved']}")
                print(f"   Duplicates: {source_result['duplicates']}")
                print(f"   Duration: {source_result['duration_seconds']}s")
            else:
                print(f"   Error: {source_result.get('error', 'Unknown')}")
            print()

        # Check database state after
        articles_after = db.query(Article).count()
        new_articles = articles_after - articles_before

        print(f"\nDatabase state AFTER scraping:")
        print(f"- Total articles in DB: {articles_after}")
        print(f"- New articles added: {new_articles}\n")

        if new_articles > 0:
            # Show some sample articles
            print("=== Sample Articles (Latest 5) ===\n")
            latest_articles = db.query(Article).order_by(
                Article.created_at.desc()
            ).limit(5).all()

            for i, article in enumerate(latest_articles, 1):
                print(f"{i}. {article.title}")
                print(f"   URL: {article.url}")
                print(f"   Source: {article.source.name if article.source else 'Unknown'}")
                print(f"   Author: {article.author}")
                print(f"   Upvotes: {article.upvotes} | Comments: {article.comments_count}")
                print(f"   Tags: {', '.join(article.tags or [])}")
                print()

        # Final summary
        print("=== Summary ===\n")
        if result['status'] == 'success':
            print("✅ Scraping task completed successfully!")
        elif result['status'] == 'partial_success':
            print("⚠️  Scraping task completed with some errors")
        else:
            print("❌ Scraping task failed")

        print(f"\nTotal time: Check logs for duration")
        print(f"Cache hits: Should see 'Cache hit' messages in logs if running twice\n")

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def test_celery_task_trigger():
    """Test triggering the Celery task (requires Celery worker running)"""
    print("\n=== Testing Celery Task (Async) ===\n")

    try:
        from app.tasks.scraping import scrape_all_sources

        print("Triggering Celery task...")
        task = scrape_all_sources.delay()

        print(f"✅ Task triggered successfully!")
        print(f"Task ID: {task.id}")
        print(f"Task state: {task.state}")
        print("\nTo check status:")
        print(f"  from celery.result import AsyncResult")
        print(f"  result = AsyncResult('{task.id}')")
        print(f"  print(result.state, result.result)")
        print("\nMake sure Celery worker is running:")
        print("  poetry run celery -A app.tasks.celery_app worker --loglevel=info")

    except Exception as e:
        print(f"❌ Error triggering Celery task: {e}")
        print("\nMake sure:")
        print("1. Redis is running (docker-compose up -d)")
        print("2. Celery worker is running")
        import traceback
        traceback.print_exc()


async def main():
    """Run tests"""
    # Test direct call (doesn't require Celery worker)
    await test_scraping_task()

    # Test Celery task trigger (requires Celery worker)
    # Uncomment to test:
    # test_celery_task_trigger()


if __name__ == '__main__':
    asyncio.run(main())
