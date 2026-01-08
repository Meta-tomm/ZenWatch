# Claude + Data Analytics Scoring Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refocus keyword scoring on Claude AI and Data Analytics, with combo bonus multiplier when both appear together.

**Architecture:** Modify seed keywords to focus on Claude + Data tools, add progressive multiplier in scorer when Claude + data tools are detected together.

**Tech Stack:** Python, spaCy, SQLAlchemy

---

## Overview

Replace current AI-focused keywords (GPT-4, Gemini, etc.) with Claude-only + Data Analytics focus. Add bonus scoring when articles mention Claude alongside data tools.

## New Keywords

### AI Model (Claude Only)
| Keyword | Category | Weight |
|---------|----------|--------|
| claude | ai-model | 4.0 |
| anthropic | ai-model | 3.5 |
| claude code | ai-model | 4.0 |
| claude sonnet | ai-model | 3.5 |
| claude opus | ai-model | 3.5 |

### Data Tools
| Keyword | Category | Weight |
|---------|----------|--------|
| power bi | data-tools | 3.0 |
| sql | data-tools | 2.5 |
| excel | data-tools | 2.0 |
| python | data-tools | 2.5 |
| pandas | data-tools | 2.5 |
| tableau | data-tools | 3.0 |
| data analyst | data-role | 3.5 |
| data science | data-role | 3.0 |
| etl | data-tools | 2.5 |
| bigquery | data-tools | 2.5 |
| snowflake | data-tools | 2.5 |
| dbt | data-tools | 2.5 |
| jupyter | data-tools | 2.0 |
| numpy | data-tools | 2.0 |
| matplotlib | data-tools | 2.0 |

### Removed Keywords
- gpt-4, gpt-5, gemini, mistral, llama (other AI models)
- langchain, llamaindex, autogpt, crewai (agent frameworks)
- openai, huggingface (other companies)
- mcp, function calling, tool use, agentic, rag (AI concepts)

## Combo Multiplier System

### Logic
When an article mentions Claude AND data tools together, apply a progressive multiplier:

| Data Tools Count | Multiplier | Bonus |
|------------------|------------|-------|
| 0 | x1.0 | No bonus |
| 1 | x1.3 | +30% |
| 2 | x1.5 | +50% |
| 3+ | x2.0 | +100% |

### Claude Keywords (trigger combo)
```python
CLAUDE_KEYWORDS = ["claude", "anthropic", "claude code", "claude sonnet", "claude opus"]
```

### Data Tools (count for multiplier)
```python
DATA_TOOLS = [
    "power bi", "sql", "excel", "python", "pandas", "tableau",
    "data analyst", "data science", "etl", "bigquery",
    "snowflake", "dbt", "jupyter", "numpy", "matplotlib"
]
```

### Examples

| Article Title | Base Score | Combo | Final Score |
|---------------|-----------|-------|-------------|
| "Power BI dashboard tips" | 45 | x1.0 | 45 |
| "Claude AI news" | 50 | x1.0 | 50 |
| "Using Claude for Power BI" | 60 | x1.3 | 78 |
| "Claude + SQL + Excel" | 55 | x1.5 | 82 |
| "Claude for Data Science with Python and Pandas" | 65 | x2.0 | 100 |

---

## Implementation Tasks

### Task 1: Update seed_keywords.py

**Files:**
- Modify: `backend/app/scripts/seed_keywords.py`

**Steps:**
1. Replace INITIAL_KEYWORDS list with new Claude + Data focused keywords
2. Add --reset flag to clear old keywords before seeding

### Task 2: Add combo multiplier to scorer.py

**Files:**
- Modify: `backend/app/nlp/scorer.py`

**Steps:**
1. Add CLAUDE_KEYWORDS and DATA_TOOLS constants at module level
2. Add `_calculate_combo_multiplier(self, text_lower: str) -> float` method
3. Apply multiplier in `score_article()` after base score calculation
4. Add `combo_multiplier` and `combo_reason` to return dict

### Task 3: Run migration and re-seed

**Steps:**
1. Run seed script with reset flag to update database
2. Verify new keywords in database

### Task 4: Add tests

**Files:**
- Create: `backend/tests/test_nlp/test_combo_scoring.py`

**Test cases:**
- Article with Claude only -> multiplier 1.0
- Article with data tool only -> multiplier 1.0
- Article with Claude + 1 data tool -> multiplier 1.3
- Article with Claude + 2 data tools -> multiplier 1.5
- Article with Claude + 3+ data tools -> multiplier 2.0

---

## API Response Changes

### Before
```json
{
    "overall_score": 60.0,
    "category": "models",
    "matched_keywords": [...],
    "scores": {"exact_match": 40, "semantic": 35, "tfidf": 45}
}
```

### After
```json
{
    "overall_score": 78.0,
    "combo_multiplier": 1.3,
    "combo_reason": "claude + 1 data tool (power bi)",
    "category": "data-tools",
    "matched_keywords": [...],
    "scores": {"exact_match": 40, "semantic": 35, "tfidf": 45}
}
```

---

## Success Criteria

- [ ] Old AI model keywords removed from database
- [ ] New Claude + Data keywords seeded
- [ ] Combo multiplier correctly applied
- [ ] API returns combo_multiplier field
- [ ] All test cases pass
