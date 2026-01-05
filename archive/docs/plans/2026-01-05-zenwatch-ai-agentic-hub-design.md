# ZenWatch AI Agentic Hub - Design Document

**Date**: 2026-01-05
**Status**: Approved
**Author**: Tom

## Vision

Transformer ZenWatch en LA plateforme de reference pour suivre l'ecosysteme IA agentique.

## Scope

### Domaines couverts
- Agents IA (Claude, GPT, LangChain, AutoGPT, CrewAI)
- MCP / Plugins / Extensions (tool-use, actions)
- Frameworks & SDKs (LangChain, LlamaIndex, Semantic Kernel)
- Modeles, benchmarks, recherche academique

### Audience cible
- Developpeurs (hands-on, veulent du code)
- Tech leads / CTOs (comparatifs, tendances)
- Passionnes IA (news digestibles)

## Architecture

### Phase 1 - Keywords IA (Terminal 1)

Creer `backend/app/scripts/seed_keywords.py` avec:

```python
INITIAL_KEYWORDS = [
    # Frameworks & Tools
    {"keyword": "langchain", "category": "frameworks", "weight": 2.5},
    {"keyword": "llamaindex", "category": "frameworks", "weight": 2.5},
    {"keyword": "autogpt", "category": "agents", "weight": 2.5},
    {"keyword": "crewai", "category": "agents", "weight": 2.5},
    {"keyword": "semantic kernel", "category": "frameworks", "weight": 2.0},

    # Models & Providers
    {"keyword": "claude", "category": "models", "weight": 3.0},
    {"keyword": "gpt-4", "category": "models", "weight": 3.0},
    {"keyword": "gpt-5", "category": "models", "weight": 3.0},
    {"keyword": "gemini", "category": "models", "weight": 2.5},
    {"keyword": "mistral", "category": "models", "weight": 2.5},
    {"keyword": "llama", "category": "models", "weight": 2.5},

    # Concepts
    {"keyword": "mcp", "category": "concepts", "weight": 3.0},
    {"keyword": "function calling", "category": "concepts", "weight": 2.5},
    {"keyword": "tool use", "category": "concepts", "weight": 2.5},
    {"keyword": "agentic", "category": "concepts", "weight": 3.0},
    {"keyword": "rag", "category": "concepts", "weight": 2.5},
    {"keyword": "fine-tuning", "category": "concepts", "weight": 2.0},
    {"keyword": "prompt engineering", "category": "concepts", "weight": 2.0},

    # Companies
    {"keyword": "openai", "category": "companies", "weight": 3.0},
    {"keyword": "anthropic", "category": "companies", "weight": 3.0},
    {"keyword": "huggingface", "category": "companies", "weight": 2.5},
    {"keyword": "ollama", "category": "tools", "weight": 2.0},

    # General
    {"keyword": "llm", "category": "general", "weight": 2.0},
    {"keyword": "agents", "category": "general", "weight": 2.5},
]
```

### Phase 2 - Arxiv Scraper (Terminal 2)

Creer `backend/app/scrapers/plugins/arxiv.py`:

- API OAI-PMH (gratuite, pas de cle requise)
- Categories: cs.AI, cs.CL, cs.LG, cs.MA (multi-agent)
- Filtrage par keywords dans titre/abstract
- Retourne: titre, auteurs, abstract, lien PDF, date

### Phase 3 - Official Blogs Scraper (Terminal 3)

Creer `backend/app/scrapers/plugins/official_blogs.py`:

Sources RSS/HTML:
- OpenAI Blog: https://openai.com/blog/rss.xml
- Anthropic News: https://www.anthropic.com/news (HTML parsing)
- Google DeepMind: https://deepmind.google/blog/rss.xml
- Meta AI: https://ai.meta.com/blog/ (HTML parsing)

## Criteres de succes

1. Couverture complete de l'ecosysteme IA agentique
2. Moins de 10 min/jour pour tout savoir
3. Zero annonce majeure ratee

## Prochaines etapes (futures)

- Twitter via Nitter (liste fixe de comptes)
- Hugging Face (nouveaux modeles)
- Newsletters (The Rundown AI, TLDR AI)
- Systeme de ranking communautaire
