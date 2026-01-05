"""
Celery tasks for article scoring
"""

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import Article, Keyword
from app.nlp import ArticleScorer, ArticleSummarizer
from app.utils.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(name="score_articles")
def score_articles(article_ids: list[int] = None):
    """
    Score des articles avec NLP

    Args:
        article_ids: Liste d'IDs d'articles à scorer (si None, score les non-scorés)

    Returns:
        Dict avec statistiques
    """
    db = SessionLocal()

    try:
        # Fetch active keywords
        keywords = db.query(Keyword).filter(Keyword.is_active == True).all()

        if not keywords:
            logger.warning("No active keywords found - skipping scoring")
            return {"status": "skipped", "reason": "no_keywords"}

        keyword_data = [
            {
                "keyword": kw.keyword,
                "weight": kw.weight,
                "category": kw.category
            }
            for kw in keywords
        ]

        # Fetch articles to score
        if article_ids:
            articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
        else:
            # Score articles without score or with score = 0
            articles = db.query(Article).filter(
                (Article.score == None) | (Article.score == 0)
            ).limit(500).all()  # Process up to 500 articles at a time

        if not articles:
            logger.info("No articles to score")
            return {"status": "success", "articles_scored": 0}

        # Initialize scorer
        scorer = ArticleScorer(language="en")  # TODO: detect language per article

        scored_count = 0
        for article in articles:
            try:
                text = f"{article.title} {article.content or ''}"

                # Score article
                result = scorer.score_article(text, keyword_data)

                # Update article - Convert NumPy types to Python natives
                article.score = float(result["overall_score"])
                article.category = str(result["category"])

                scored_count += 1

                if scored_count % 10 == 0:
                    logger.info(f"Scored {scored_count}/{len(articles)} articles")

            except Exception as e:
                logger.error(f"Error scoring article {article.id}: {e}")
                continue

        db.commit()
        logger.info(f"Scoring complete: {scored_count} articles scored")

        return {
            "status": "success",
            "articles_scored": scored_count,
            "total_articles": len(articles)
        }

    except Exception as e:
        logger.error(f"Error in score_articles task: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        db.close()


@celery_app.task(name="rescore_all_articles")
def rescore_all_articles(force_all: bool = True):
    """
    Re-score all articles with current keywords

    Args:
        force_all: If True, rescore ALL articles regardless of current score

    Returns:
        Dict avec statistiques
    """
    db = SessionLocal()

    try:
        # Fetch active keywords
        keywords = db.query(Keyword).filter(Keyword.is_active == True).all()

        if not keywords:
            logger.warning("No active keywords found - skipping scoring")
            return {"status": "skipped", "reason": "no_keywords"}

        keyword_data = [
            {
                "keyword": kw.keyword,
                "weight": kw.weight,
                "category": kw.category
            }
            for kw in keywords
        ]

        logger.info(f"Rescoring with {len(keyword_data)} active keywords")

        # Fetch all articles
        if force_all:
            articles = db.query(Article).all()
        else:
            articles = db.query(Article).filter(
                (Article.score == None) | (Article.score == 0)
            ).all()

        if not articles:
            logger.info("No articles to rescore")
            return {"status": "success", "articles_scored": 0}

        logger.info(f"Rescoring {len(articles)} articles...")

        # Initialize scorer
        scorer = ArticleScorer(language="en")

        scored_count = 0
        for article in articles:
            try:
                text = f"{article.title} {article.content or ''}"

                # Score article
                result = scorer.score_article(text, keyword_data)

                # Update article
                article.score = float(result["overall_score"])
                article.category = str(result["category"])

                scored_count += 1

                if scored_count % 50 == 0:
                    logger.info(f"Rescored {scored_count}/{len(articles)} articles")
                    db.commit()  # Commit in batches

            except Exception as e:
                logger.error(f"Error scoring article {article.id}: {e}")
                continue

        db.commit()
        logger.info(f"Rescore complete: {scored_count} articles rescored")

        return {
            "status": "success",
            "articles_scored": scored_count,
            "total_articles": len(articles),
            "keywords_used": len(keyword_data)
        }

    except Exception as e:
        logger.error(f"Error in rescore_all_articles task: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        db.close()


@celery_app.task(name="summarize_articles")
def summarize_articles(article_ids: list[int] = None):
    """
    Génère des résumés IA pour les articles

    Args:
        article_ids: Liste d'IDs d'articles à résumer (si None, résume les non-résumés)

    Returns:
        Dict avec statistiques
    """
    db = SessionLocal()

    try:
        # Fetch articles to summarize
        if article_ids:
            articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
        else:
            # Summarize articles without summary
            articles = db.query(Article).filter(
                Article.summary == None,
                Article.content.isnot(None)
            ).limit(50).all()  # Limit to avoid API quota

        if not articles:
            logger.info("No articles to summarize")
            return {"status": "success", "articles_summarized": 0}

        # Initialize summarizer
        summarizer = ArticleSummarizer()

        if not summarizer.client:
            logger.warning("Claude API not configured - skipping summarization")
            return {"status": "skipped", "reason": "no_api_key"}

        summarized_count = 0
        for article in articles:
            try:
                # Synchronous call - Anthropic SDK handles async internally
                summary = summarizer.summarize_sync(
                    article.title,
                    article.content,
                    max_length=200
                )

                if summary:
                    article.summary = summary
                    summarized_count += 1

                if summarized_count % 5 == 0:
                    logger.info(f"Summarized {summarized_count}/{len(articles)} articles")

            except Exception as e:
                logger.error(f"Error summarizing article {article.id}: {e}")
                continue

        db.commit()
        logger.info(f"Summarization complete: {summarized_count} articles summarized")

        return {
            "status": "success",
            "articles_summarized": summarized_count,
            "total_articles": len(articles)
        }

    except Exception as e:
        logger.error(f"Error in summarize_articles task: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        db.close()
