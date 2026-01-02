"""
Article Scorer - NLP-based relevance scoring
Combine plusieurs approches pour scorer les articles selon les mots-clés
"""

from typing import List, Dict
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ArticleScorer:
    """Score les articles selon les mots-clés avec 3 approches combinées"""

    def __init__(self, language: str = "en"):
        """
        Initialize scorer with spaCy model

        Args:
            language: Language code ("en" or "fr")
        """
        self.language = language
        try:
            if language == "fr":
                self.nlp = spacy.load("fr_core_news_lg")
            else:
                self.nlp = spacy.load("en_core_web_lg")
            logger.info(f"Loaded spaCy model for language: {language}")
        except OSError:
            logger.error(f"spaCy model not found for {language}")
            raise

        self.tfidf = TfidfVectorizer(
            max_features=500,
            stop_words='english' if language == "en" else None,
            ngram_range=(1, 2)
        )

    def score_article(self, text: str, keywords: List[Dict]) -> Dict:
        """
        Score un article selon les mots-clés

        Args:
            text: Texte de l'article (title + content)
            keywords: Liste de dicts {"keyword": str, "weight": float, "category": str}

        Returns:
            {
                "overall_score": float (0-100),
                "category": str,
                "matched_keywords": List[Dict],
                "scores": {
                    "exact_match": float,
                    "semantic": float,
                    "tfidf": float
                }
            }
        """
        if not text or not keywords:
            return {
                "overall_score": 0.0,
                "category": "uncategorized",
                "matched_keywords": [],
                "scores": {'exact_match': 0.0, 'semantic': 0.0, 'tfidf': 0.0}
            }

        text_lower = text.lower()
        doc = self.nlp(text)

        matched_keywords = []
        scores_detail = {'exact_match': 0.0, 'semantic': 0.0, 'tfidf': 0.0}

        # 1. Exact Match Score (40% weight)
        exact_score = self._exact_match_score(text_lower, keywords)
        scores_detail["exact_match"] = exact_score

        # 2. Semantic Similarity Score (30% weight) - spaCy embeddings
        semantic_score = self._semantic_similarity_score(doc, keywords)
        scores_detail["semantic"] = semantic_score

        # 3. TF-IDF Cosine Similarity Score (30% weight)
        tfidf_score = self._tfidf_score(text, keywords)
        scores_detail["tfidf"] = tfidf_score

        # Overall score: weighted average
        overall_score = (
            exact_score * 0.4 +
            semantic_score * 0.3 +
            tfidf_score * 0.3
        )

        # Determine category (most relevant keyword category)
        category = self._determine_category(text_lower, keywords)

        # Identify matched keywords
        for kw in keywords:
            if kw["keyword"].lower() in text_lower:
                matched_keywords.append({
                    "keyword": kw["keyword"],
                    "category": kw.get("category", "other"),
                    "weight": kw.get("weight", 1.0)
                })

        return {
            "overall_score": min(100.0, overall_score),  # Cap à 100
            "category": category,
            "matched_keywords": matched_keywords,
            "scores": scores_detail
        }

    def _exact_match_score(self, text_lower: str, keywords: List[Dict]) -> float:
        """
        Score basé sur la présence exacte des mots-clés

        Returns:
            Score 0-100
        """
        total_weight = 0.0
        matched_weight = 0.0

        for kw in keywords:
            weight = kw.get("weight", 1.0)
            total_weight += weight

            if kw["keyword"].lower() in text_lower:
                matched_weight += weight

        if total_weight == 0:
            return 0.0

        return (matched_weight / total_weight) * 100

    def _semantic_similarity_score(self, doc: spacy.tokens.Doc, keywords: List[Dict]) -> float:
        """
        Score basé sur la similarité sémantique avec spaCy embeddings

        Returns:
            Score 0-100
        """
        if not doc.has_vector:
            return 0.0

        similarities = []

        for kw in keywords:
            kw_doc = self.nlp(kw["keyword"])
            if kw_doc.has_vector:
                sim = doc.similarity(kw_doc)
                weight = kw.get("weight", 1.0)
                similarities.append(sim * weight)

        if not similarities:
            return 0.0

        # Average similarity weighted
        avg_similarity = np.mean(similarities)
        return max(0.0, avg_similarity * 100)

    def _tfidf_score(self, text: str, keywords: List[Dict]) -> float:
        """
        Score basé sur TF-IDF cosine similarity

        Returns:
            Score 0-100
        """
        try:
            # Build corpus: article + keywords
            corpus = [text] + [kw["keyword"] for kw in keywords]

            # Fit TF-IDF
            tfidf_matrix = self.tfidf.fit_transform(corpus)

            # Calculate cosine similarity between article and each keyword
            article_vec = tfidf_matrix[0:1]
            keyword_vecs = tfidf_matrix[1:]

            similarities = cosine_similarity(article_vec, keyword_vecs).flatten()

            # Weight by keyword weight
            weighted_sims = []
            for i, kw in enumerate(keywords):
                weight = kw.get("weight", 1.0)
                weighted_sims.append(similarities[i] * weight)

            if not weighted_sims:
                return 0.0

            avg_similarity = np.mean(weighted_sims)
            return max(0.0, avg_similarity * 100)

        except Exception as e:
            logger.warning(f"TF-IDF scoring failed: {e}")
            return 0.0

    def _determine_category(self, text_lower: str, keywords: List[Dict]) -> str:
        """
        Détermine la catégorie dominante de l'article

        Returns:
            Category string (healthtech, web3, dev, etc.)
        """
        category_scores = {}

        for kw in keywords:
            if kw["keyword"].lower() in text_lower:
                category = kw.get("category", "other")
                weight = kw.get("weight", 1.0)
                category_scores[category] = category_scores.get(category, 0.0) + weight

        if not category_scores:
            return "other"

        # Return category with highest score
        return max(category_scores, key=category_scores.get)
