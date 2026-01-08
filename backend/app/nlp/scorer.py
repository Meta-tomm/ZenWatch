"""
Article Scorer - NLP-based relevance scoring
Combine plusieurs approches pour scorer les articles selon les mots-clés
"""

from typing import List, Dict, Tuple
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Keywords that trigger combo bonus (Claude AI)
CLAUDE_KEYWORDS = ["claude", "anthropic", "claude code", "claude sonnet", "claude opus"]

# Data tools that count toward combo multiplier
DATA_TOOLS = [
    "power bi", "sql", "excel", "python", "pandas", "tableau",
    "data analyst", "data science", "etl", "bigquery",
    "snowflake", "dbt", "jupyter", "numpy", "matplotlib"
]


class ArticleScorer:
    """Score les articles selon les mots-clés avec 3 approches combinées"""

    def __init__(self, language: str = "en"):
        """
        Initialize scorer with spaCy model

        Args:
            language: Language code ("en" or "fr")
        """
        self.language = language
        # Try models in order: lg > md > sm (best quality first)
        models = {
            "fr": ["fr_core_news_lg", "fr_core_news_md", "fr_core_news_sm"],
            "en": ["en_core_web_lg", "en_core_web_md", "en_core_web_sm"]
        }
        model_list = models.get(language, models["en"])

        for model_name in model_list:
            try:
                self.nlp = spacy.load(model_name)
                logger.info(f"Loaded spaCy model: {model_name}")
                break
            except OSError:
                continue
        else:
            logger.error(f"No spaCy model found for {language}")
            raise OSError(f"No spaCy model available for {language}")

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

        # Apply combo multiplier (Claude + Data tools)
        combo_multiplier, combo_reason, matched_data_tools = self._calculate_combo_multiplier(text_lower)
        overall_score = min(100.0, overall_score * combo_multiplier)

        return {
            "overall_score": overall_score,
            "category": category,
            "matched_keywords": matched_keywords,
            "scores": scores_detail,
            "combo_multiplier": combo_multiplier,
            "combo_reason": combo_reason,
            "matched_data_tools": matched_data_tools
        }

    def _exact_match_score(self, text_lower: str, keywords: List[Dict]) -> float:
        """
        Score based on matched keywords weight sum.
        Uses logarithmic scaling: each match contributes significantly.

        Returns:
            Score 0-100
        """
        matched_weight = 0.0
        match_count = 0

        for kw in keywords:
            if kw["keyword"].lower() in text_lower:
                weight = kw.get("weight", 1.0)
                matched_weight += weight
                match_count += 1

        if match_count == 0:
            return 0.0

        # Score formula: base score from matches + bonus for weight
        # 1 match = 20, 2 matches = 35, 3 matches = 47, 5 matches = 65, 10 matches = 86
        base_score = min(100, 20 * np.log2(match_count + 1))

        # Weight bonus: high-weight keyword matches boost score
        weight_bonus = min(30, matched_weight * 3)

        return min(100.0, base_score + weight_bonus)

    def _semantic_similarity_score(self, doc: spacy.tokens.Doc, keywords: List[Dict]) -> float:
        """
        Score based on TOP 5 semantic similarities (best matches).

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

        # Use TOP 5 similarities instead of average (focus on best matches)
        top_n = sorted(similarities, reverse=True)[:5]
        avg_top_similarity = np.mean(top_n)

        return max(0.0, min(100.0, avg_top_similarity * 100))

    def _tfidf_score(self, text: str, keywords: List[Dict]) -> float:
        """
        Score based on TOP 5 TF-IDF cosine similarities.

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

            # Use TOP 5 similarities instead of average
            top_n = sorted(weighted_sims, reverse=True)[:5]
            avg_top_similarity = np.mean(top_n)

            return max(0.0, min(100.0, avg_top_similarity * 100))

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

    def _calculate_combo_multiplier(self, text_lower: str) -> Tuple[float, str, List[str]]:
        """
        Calculate combo multiplier when Claude + data tools are present together.

        Progressive multiplier:
        - 1 data tool: x1.3
        - 2 data tools: x1.5
        - 3+ data tools: x2.0

        Args:
            text_lower: Lowercased article text

        Returns:
            Tuple of (multiplier, reason, matched_data_tools)
        """
        # Check if any Claude keyword is present
        has_claude = any(kw in text_lower for kw in CLAUDE_KEYWORDS)

        if not has_claude:
            return 1.0, "no combo", []

        # Count matched data tools
        matched_tools = [tool for tool in DATA_TOOLS if tool in text_lower]
        tool_count = len(matched_tools)

        if tool_count >= 3:
            return 2.0, f"claude + {tool_count} data tools", matched_tools
        elif tool_count == 2:
            return 1.5, f"claude + 2 data tools", matched_tools
        elif tool_count == 1:
            return 1.3, f"claude + 1 data tool", matched_tools
        else:
            return 1.0, "claude only", []
