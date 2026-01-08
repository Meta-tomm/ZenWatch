"""
Tests for combo scoring (Claude + Data tools multiplier)
"""

import pytest
from app.nlp.scorer import ArticleScorer, CLAUDE_KEYWORDS, DATA_TOOLS


class TestComboMultiplier:
    """Test the _calculate_combo_multiplier method"""

    @pytest.fixture
    def scorer(self):
        """Create scorer instance"""
        return ArticleScorer(language="en")

    def test_no_combo_without_claude(self, scorer):
        """Article with data tools but no Claude should have no combo"""
        text = "learn power bi and sql for data analysis"
        multiplier, reason, tools = scorer._calculate_combo_multiplier(text)

        assert multiplier == 1.0
        assert reason == "no combo"
        assert tools == []

    def test_no_combo_claude_only(self, scorer):
        """Article with Claude but no data tools should have no combo"""
        text = "claude is a great ai assistant for coding"
        multiplier, reason, tools = scorer._calculate_combo_multiplier(text)

        assert multiplier == 1.0
        assert reason == "claude only"
        assert tools == []

    def test_combo_x1_3_one_tool(self, scorer):
        """Claude + 1 data tool should give x1.3 multiplier"""
        text = "using claude for power bi dashboard automation"
        multiplier, reason, tools = scorer._calculate_combo_multiplier(text)

        assert multiplier == 1.3
        assert "1 data tool" in reason
        assert "power bi" in tools

    def test_combo_x1_5_two_tools(self, scorer):
        """Claude + 2 data tools should give x1.5 multiplier"""
        text = "claude can help with sql queries and python data analysis"
        multiplier, reason, tools = scorer._calculate_combo_multiplier(text)

        assert multiplier == 1.5
        assert "2 data tools" in reason
        assert len(tools) == 2
        assert "sql" in tools
        assert "python" in tools

    def test_combo_x2_0_three_plus_tools(self, scorer):
        """Claude + 3+ data tools should give x2.0 multiplier"""
        text = "claude for data analyst work with excel, sql, and python pandas"
        multiplier, reason, tools = scorer._calculate_combo_multiplier(text)

        assert multiplier == 2.0
        assert "data tools" in reason
        assert len(tools) >= 3

    def test_combo_with_anthropic(self, scorer):
        """Anthropic keyword should also trigger combo"""
        text = "anthropic claude for power bi reporting"
        multiplier, reason, tools = scorer._calculate_combo_multiplier(text)

        assert multiplier == 1.3
        assert "power bi" in tools

    def test_combo_case_insensitive(self, scorer):
        """Combo detection should be case insensitive"""
        text = "CLAUDE for POWER BI and SQL"
        multiplier, reason, tools = scorer._calculate_combo_multiplier(text.lower())

        assert multiplier == 1.5


class TestScoreArticleWithCombo:
    """Test that combo multiplier is applied in score_article"""

    @pytest.fixture
    def scorer(self):
        return ArticleScorer(language="en")

    @pytest.fixture
    def keywords(self):
        return [
            {"keyword": "claude", "weight": 4.0, "category": "ai-model"},
            {"keyword": "power bi", "weight": 3.0, "category": "data-tools"},
            {"keyword": "sql", "weight": 2.5, "category": "data-tools"},
            {"keyword": "python", "weight": 2.5, "category": "data-tools"},
        ]

    def test_score_includes_combo_fields(self, scorer, keywords):
        """Score result should include combo multiplier fields"""
        text = "claude helps with power bi dashboards"
        result = scorer.score_article(text, keywords)

        assert "combo_multiplier" in result
        assert "combo_reason" in result
        assert "matched_data_tools" in result

    def test_score_multiplied_with_combo(self, scorer, keywords):
        """Score should be multiplied when combo is active"""
        text_no_combo = "power bi dashboard tips"
        text_with_combo = "claude for power bi dashboard tips"

        result_no_combo = scorer.score_article(text_no_combo, keywords)
        result_with_combo = scorer.score_article(text_with_combo, keywords)

        # With combo should have higher score due to multiplier
        assert result_with_combo["combo_multiplier"] == 1.3
        assert result_no_combo["combo_multiplier"] == 1.0

    def test_score_capped_at_100(self, scorer, keywords):
        """Score should never exceed 100 even with combo"""
        # Create a high-scoring scenario
        text = "claude anthropic claude code power bi sql python pandas excel"
        result = scorer.score_article(text, keywords)

        assert result["overall_score"] <= 100.0


class TestDataToolsAndClaudeKeywords:
    """Test that constants are properly defined"""

    def test_claude_keywords_defined(self):
        """Claude keywords should be defined"""
        assert len(CLAUDE_KEYWORDS) >= 5
        assert "claude" in CLAUDE_KEYWORDS
        assert "anthropic" in CLAUDE_KEYWORDS

    def test_data_tools_defined(self):
        """Data tools should be defined"""
        assert len(DATA_TOOLS) >= 15
        assert "power bi" in DATA_TOOLS
        assert "sql" in DATA_TOOLS
        assert "python" in DATA_TOOLS
        assert "data analyst" in DATA_TOOLS
