# TechWatch AI - Plateforme de Veille Technologique Intelligente

## Description du projet

TechWatch est une plateforme de veille technologique personnalisée qui automatise la collecte, l'analyse et la présentation d'informations tech pertinentes.
Le système scrappe des sources multiples (Reddit, HackerNews, Dev.to, Medium, GitHub Trending), utilise du NLP pour scorer les articles selon les mots-clés de l'utilisateur, génère des résumés IA via l'API Claude, et présente les données via des dashboards Power BI interactifs.
L'objectif est de remplacer 2h de veille manuelle quotidienne par un système intelligent qui livre les top articles pertinents chaque matin.

## Stack technique

### Frontend (Dashboard Web)

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS + shadcn/ui (Composants)
- **State Management**: Zustand (Global), TanStack Query (Server state)
- **Forms**: React Hook Form + Zod (Validation)
- **Charts**: Recharts (graphiques frontend)
- **Icons**: Lucide React

### Backend (API & ETL)

- **Language**: Python 3.11+
- **Framework**: FastAPI (API REST moderne)
- **ORM**: SQLAlchemy 2.0 (avec typage)
- **Validation**: Pydantic V2
- **Database**: PostgreSQL 16 (driver: asyncpg)
- **Cache & Queue**: Redis 7
- **Task Queue**: Celery + Redis (scraping automatique)
- **HTTP Client**: httpx (async)
- **AI Integration**: Anthropic API (Claude Sonnet 4)
- **NLP**: spaCy (fr_core_news_lg / en_core_web_lg)
- **ML Scoring**: scikit-learn (TF-IDF, cosine similarity)

### Scraping Workers

- **Scrapers**: Modules Python async (httpx + BeautifulSoup 4)
- **Sources**:
  - Reddit (API OAuth2)
  - HackerNews (Firebase API)
  - Dev.to (API REST)
  - GitHub Trending (scraping HTML)
  - Medium (RSS)
  - Twitter/X (API v2, optionnel)

### Business Intelligence

- **Power BI Desktop**: Dashboards interactifs
- **Power BI Embedded**: Intégration dans le frontend Next.js
- **DAX**: Mesures et KPIs personnalisés
- **SQL Views**: Vues optimisées pour Power BI

### Infrastructure

- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Linting**: Ruff (Python), ESLint + Biome (TypeScript)
- **Testing**: Pytest (Backend), Vitest (Frontend)

## Architecture du projet (Monorepo)

### Structure des dossiers

```
techwatch/
├── 📂 .github/                 # CI/CD Workflows
│   └── workflows/
│       ├── backend-ci.yml
│       └── frontend-ci.yml
│
├── 📂 infra/                   # Docker, Nginx, Postgres configs
│   ├── docker-compose.yml
│   ├── postgres/
│   │   └── init.sql
│   └── nginx/
│
├── 📂 backend/                 # API Python FastAPI
│   ├── app/
│   │   ├── main.py            # Entrypoint FastAPI
│   │   ├── config.py          # Settings (Pydantic)
│   │   ├── database.py        # SQLAlchemy engine & session
│   │   │
│   │   ├── models/            # SQLAlchemy Models (Tables DB)
│   │   │   ├── __init__.py
│   │   │   ├── article.py     # Table articles
│   │   │   ├── keyword.py     # Table keywords
│   │   │   ├── source.py      # Table sources (Reddit, HN...)
│   │   │   └── user_config.py # Config utilisateur
│   │   │
│   │   ├── schemas/           # Pydantic Schemas (DTO/validation)
│   │   │   ├── __init__.py
│   │   │   ├── article.py     # ArticleResponse, ArticleCreate
│   │   │   ├── keyword.py     # KeywordCreate, KeywordUpdate
│   │   │   └── config.py      # UserConfigUpdate
│   │   │
│   │   ├── api/               # Routes API REST
│   │   │   ├── __init__.py
│   │   │   ├── deps.py        # Dependencies injection
│   │   │   ├── articles.py    # GET/POST /api/articles
│   │   │   ├── keywords.py    # CRUD mots-clés
│   │   │   ├── sources.py     # CRUD sources
│   │   │   └── analytics.py   # Stats & tendances
│   │   │
│   │   ├── scrapers/          # Modules de scraping
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # BaseScraper (classe abstraite)
│   │   │   ├── reddit.py      # RedditScraper
│   │   │   ├── hackernews.py  # HackerNewsScraper
│   │   │   ├── devto.py       # DevToScraper
│   │   │   ├── github.py      # GitHubTrendingScraper
│   │   │   ├── medium.py      # MediumRSSScraper
│   │   │   └── factory.py     # ScraperFactory (pattern)
│   │   │
│   │   ├── nlp/               # Natural Language Processing
│   │   │   ├── __init__.py
│   │   │   ├── scorer.py      # ArticleScorer (spaCy + TF-IDF)
│   │   │   ├── summarizer.py  # ArticleSummarizer (Claude API)
│   │   │   ├── categorizer.py # Auto-catégorisation
│   │   │   └── deduplicator.py # Détection doublons
│   │   │
│   │   ├── tasks/             # Celery Tasks (async jobs)
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py  # Config Celery
│   │   │   ├── scraping.py    # Task: scrape_all_sources
│   │   │   ├── scoring.py     # Task: score_articles
│   │   │   └── email.py       # Task: send_daily_digest
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py      # Logging config
│   │       └── email_sender.py # SMTP email
│   │
│   ├── alembic/               # Migrations DB
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/
│   │   ├── test_scrapers/
│   │   ├── test_nlp/
│   │   └── test_api/
│   │
│   ├── pyproject.toml         # Poetry dependencies
│   ├── Dockerfile
│   └── .env.example
│
├── 📂 frontend/                # Next.js React
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx           # Dashboard principal
│   │   ├── config/
│   │   │   └── page.tsx       # Gestion mots-clés
│   │   ├── analytics/
│   │   │   └── page.tsx       # Analytics avancées
│   │   └── api/               # API Routes Next.js
│   │       └── powerbi/       # Proxy Power BI Embedded
│   │
│   ├── components/
│   │   ├── ui/                # shadcn/ui components
│   │   ├── ArticleCard.tsx    # Carte article
│   │   ├── KeywordManager.tsx # Gestion mots-clés
│   │   ├── SourceToggle.tsx   # Toggle sources on/off
│   │   ├── TrendChart.tsx     # Graphiques tendances
│   │   └── PowerBIDashboard.tsx # Embed Power BI
│   │
│   ├── lib/
│   │   ├── api-client.ts      # Client axios pour backend
│   │   ├── utils.ts           # Helpers (cn, formatDate...)
│   │   └── validators.ts      # Zod schemas
│   │
│   ├── hooks/
│   │   ├── useArticles.ts     # TanStack Query hook
│   │   ├── useKeywords.ts
│   │   └── useTrends.ts
│   │
│   ├── store/                 # Zustand stores
│   │   ├── config-store.ts    # State config globale
│   │   └── ui-store.ts        # State UI (modals, etc)
│   │
│   ├── types/
│   │   └── index.ts           # Types TypeScript
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── 📂 database/
│   ├── init.sql               # Script initialisation
│   └── powerbi/
│       ├── views.sql          # Vues SQL pour Power BI
│       └── measures.dax       # Mesures DAX templates
│
├── 📂 powerbi/
│   ├── TechWatch.pbix         # Fichier Power BI Desktop
│   └── reports/
│       ├── daily-stats.pbix
│       └── trends.pbix
│
├── docker-compose.yml
└── README.md
```

## Schéma Base de Données PostgreSQL

### Tables principales

**sources** - Sources de scraping

```sql
- id (SERIAL PRIMARY KEY)
- name (VARCHAR) - "Reddit", "HackerNews"...
- type (VARCHAR) - "reddit", "hackernews"...
- base_url (TEXT)
- is_active (BOOLEAN)
- scrape_frequency_hours (INTEGER)
- last_scraped_at (TIMESTAMP)
- config (JSONB) - Config spécifique
- created_at, updated_at
```

**keywords** - Mots-clés utilisateur

```sql
- id (SERIAL PRIMARY KEY)
- keyword (VARCHAR) - "FHIR", "blockchain"...
- category (VARCHAR) - "healthtech", "web3"...
- weight (FLOAT) - Importance 1.0-5.0
- is_active (BOOLEAN)
- created_at, updated_at
```

**articles** - Articles scrapés et analysés

```sql
- id (SERIAL PRIMARY KEY)
- source_id (FK → sources)
- external_id (VARCHAR) - ID sur source externe
- title (TEXT)
- url (TEXT UNIQUE)
- content (TEXT)
- summary (TEXT) - Résumé généré par IA
- author (VARCHAR)
- published_at (TIMESTAMP)
- scraped_at (TIMESTAMP)
- score (FLOAT) - Score pertinence 0-100
- category (VARCHAR) - Catégorie auto-détectée
- tags (TEXT[]) - Array de tags
- language (VARCHAR)
- read_time_minutes (INTEGER)
- upvotes, comments_count (INTEGER)
- is_read, is_favorite, is_archived (BOOLEAN)
- created_at, updated_at
```

**article_keywords** - Relation N:N

```sql
- id (SERIAL PRIMARY KEY)
- article_id (FK → articles)
- keyword_id (FK → keywords)
- relevance_score (FLOAT) - Score pour ce keyword
- created_at
```

**trends** - Tendances détectées

```sql
- id (SERIAL PRIMARY KEY)
- keyword (VARCHAR)
- category (VARCHAR)
- trend_score (FLOAT) - Score de tendance
- article_count (INTEGER)
- date (DATE)
- created_at
```

**user_config** - Configuration utilisateur

```sql
- id (SERIAL PRIMARY KEY)
- email (VARCHAR)
- daily_digest_enabled (BOOLEAN)
- digest_time (TIME)
- min_score_threshold (FLOAT)
- preferred_categories (TEXT[])
- email_frequency (VARCHAR) - "daily", "weekly"
- created_at, updated_at
```

### Vues SQL pour Power BI

**vw_articles_daily_stats**

```sql
SELECT
    DATE(published_at) as date,
    category,
    COUNT(*) as article_count,
    AVG(score) as avg_score,
    SUM(CASE WHEN is_read THEN 1 ELSE 0 END) as read_count
FROM articles
GROUP BY DATE(published_at), category;
```

**vw_weekly_trends**

```sql
SELECT
    DATE_TRUNC('week', date) as week_start,
    keyword,
    AVG(trend_score) as avg_trend_score,
    SUM(article_count) as total_articles
FROM trends
GROUP BY week_start, keyword;
```

## Conventions de code

### Naming Conventions

**Python (Backend)**

- `snake_case` pour variables, fonctions, modules
- `PascalCase` pour Classes, Pydantic Models
- `SCREAMING_SNAKE_CASE` pour constantes
- Préfixe privé : `_function_name`
- Async functions : `async def fetch_articles()`

**TypeScript (Frontend)**

- `PascalCase` pour Composants React (`ArticleCard.tsx`)
- `camelCase` pour variables, fonctions
- `usePrefix` pour hooks custom (`useArticles`)
- `SCREAMING_SNAKE_CASE` pour constantes globales
- Interfaces : préfixe `I` optionnel (`IArticle` ou `Article`)

**SQL**

- Tables : `snake_case` pluriel (`articles`, `keywords`)
- Colonnes : `snake_case` (`created_at`, `is_active`)
- Vues : préfixe `vw_` (`vw_daily_stats`)
- Index : préfixe `idx_` (`idx_articles_score`)

### Structure Composant React (Exemple)

```typescript
'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, Star } from 'lucide-react';
import type { Article } from '@/types';

interface ArticleCardProps {
  article: Article;
  onToggleFavorite?: (id: string) => void;
  onMarkRead?: (id: string) => void;
}

export const ArticleCard = ({
  article,
  onToggleFavorite,
  onMarkRead
}: ArticleCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Early return si données invalides
  if (!article.title || !article.url) return null;

  return (
    <div className="border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h3 className="font-bold text-lg leading-tight">
            {article.title}
          </h3>
          <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
            <span>{article.source?.name}</span>
            <span>•</span>
            <span>{format(new Date(article.published_at), 'dd MMM yyyy')}</span>
            {article.read_time_minutes && (
              <>
                <span>•</span>
                <span>{article.read_time_minutes} min</span>
              </>
            )}
          </div>
        </div>

        {/* Score badge */}
        <Badge
          variant={article.score > 70 ? 'default' : 'secondary'}
          className="shrink-0"
        >
          {article.score.toFixed(0)}
        </Badge>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 my-3">
        <Badge variant="outline">{article.category}</Badge>
        {article.tags?.slice(0, 3).map((tag) => (
          <Badge key={tag} variant="secondary">
            {tag}
          </Badge>
        ))}
      </div>

      {/* Summary (conditionnel) */}
      {isExpanded && article.summary && (
        <p className="text-sm text-muted-foreground my-3 leading-relaxed">
          {article.summary}
        </p>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 mt-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? 'Réduire' : 'Voir résumé'}
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onToggleFavorite?.(article.id)}
        >
          <Star className={article.is_favorite ? 'fill-current' : ''} />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          asChild
        >
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="w-4 h-4" />
          </a>
        </Button>
      </div>
    </div>
  );
};
```

### Structure Service Python (Exemple)

```python
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.keyword import Keyword
from app.nlp.scorer import ArticleScorer
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ArticleService:
    """Service métier pour la gestion des articles"""

    def __init__(self, db: Session):
        self.db = db
        self.scorer = ArticleScorer()

    async def get_articles(
        self,
        category: Optional[str] = None,
        min_score: float = 0.0,
        limit: int = 50,
        offset: int = 0
    ) -> List[Article]:
        """
        Récupère les articles avec filtres

        Args:
            category: Filtrer par catégorie
            min_score: Score minimum
            limit: Nombre max de résultats
            offset: Offset pour pagination

        Returns:
            Liste d'articles triés par score décroissant
        """
        query = self.db.query(Article).filter(
            Article.score >= min_score,
            Article.is_archived == False
        )

        if category:
            query = query.filter(Article.category == category)

        articles = query.order_by(
            Article.score.desc()
        ).limit(limit).offset(offset).all()

        logger.info(f"Retrieved {len(articles)} articles")
        return articles

    async def score_article(
        self,
        article: Article,
        keywords: List[Keyword]
    ) -> float:
        """
        Score un article selon les mots-clés

        Args:
            article: Article à scorer
            keywords: Liste des mots-clés actifs

        Returns:
            Score de pertinence 0-100
        """
        try:
            text = f"{article.title} {article.content or ''}"
            keyword_data = [
                {
                    "keyword": kw.keyword,
                    "weight": kw.weight,
                    "category": kw.category
                }
                for kw in keywords
            ]

            result = self.scorer.score_article(text, keyword_data)

            # Update article
            article.score = result["overall_score"]
            article.category = result["category"]
            self.db.commit()

            return result["overall_score"]

        except Exception as e:
            logger.error(f"Error scoring article {article.id}: {e}")
            self.db.rollback()
            raise
```

## Gestion d'Erreur & Sécurité

### Python (Backend)

**Gestion d'erreurs**

```python
# ❌ MAUVAIS
def fetch_data():
    response = requests.get(url)
    return response.json()

# ✅ BON
async def fetch_data():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                timeout=30.0,
                headers={"User-Agent": settings.USER_AGENT}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

**Validation Pydantic**

```python
from pydantic import BaseModel, Field, field_validator

class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    url: str = Field(..., pattern=r'^https?://')
    content: Optional[str] = Field(None, max_length=50000)

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
```

### TypeScript (Frontend)

**Error Boundaries**

```typescript
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service (Sentry, etc.)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 border border-red-500 rounded">
          <h2 className="text-red-500 font-bold">Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**Validation Zod**

```typescript
import { z } from "zod";

export const articleSchema = z.object({
  title: z.string().min(1).max(500),
  url: z.string().url(),
  content: z.string().max(50000).optional(),
  score: z.number().min(0).max(100),
  category: z.enum(["healthtech", "blockchain", "dev", "other"]),
});

export type Article = z.infer<typeof articleSchema>;
```

### Sécurité

**Secrets Management**

```bash
# .env (JAMAIS commité)
DATABASE_URL=postgresql://user:password@localhost:5432/techwatch
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-xxx
SECRET_KEY=xxx

# .env.example (commité)
DATABASE_URL=postgresql://user:password@localhost:5432/techwatch
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

**CORS Configuration**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**SQL Injection Prevention**

```python
# ❌ DANGEREUX
query = f"SELECT * FROM articles WHERE title = '{user_input}'"

# ✅ SÉCURISÉ (paramétrisé)
query = select(Article).where(Article.title == user_input)
```

## Instructions pour l'IA (Claude)

### Comportement général

1. **Context Awareness**: Toujours vérifier dans quel dossier tu travailles (`backend/`, `frontend/`, `database/`, `powerbi/`)

2. **Type Safety Strict**:
   - Python : Utiliser les type hints partout
   - TypeScript : ZERO `any`, utiliser les types stricts
   - SQL : Utiliser les types PostgreSQL appropriés

3. **Performance First**:
   - Backend : Async/await partout (httpx, asyncpg)
   - Frontend : Lazy loading, pagination, React.memo
   - DB : Index sur colonnes filtrées, vues matérialisées si besoin

4. **Testing Mindset**:
   - Écrire des tests pour la logique critique
   - Mock les appels API externes
   - Tests unitaires + tests d'intégration

### Ce que tu DOIS faire

✅ Proposer des solutions modulaires (1 fichier = 1 responsabilité)
✅ Utiliser les composants shadcn/ui existants
✅ Documenter les fonctions complexes (docstrings Python, JSDoc TypeScript)
✅ Logger les erreurs avec contexte
✅ Valider les inputs (Pydantic, Zod)
✅ Gérer les cas limites (données nulles, timeout réseau)
✅ Suivre les conventions de nommage du projet

### Ce que tu NE DOIS PAS faire

❌ Modifier les configs Docker/Compose sans demande explicite
❌ Introduire de nouvelles dépendances lourdes sans justification
❌ Laisser des `console.log`, `print()`, `fmt.Println` de debug
❌ Utiliser `any` en TypeScript ou ignorer les type hints Python
❌ Faire des appels synchrones bloquants (toujours async)
❌ Hardcoder des secrets ou tokens
❌ Créer des fichiers de +500 lignes sans découpage logique

### Patterns recommandés

**Repository Pattern (Backend)**

```python
# repositories/article_repository.py
class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, article_id: int) -> Optional[Article]:
        return self.db.query(Article).filter(Article.id == article_id).first()

    async def create(self, article: Article) -> Article:
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article
```

**Custom Hooks (Frontend)**

```typescript
// hooks/useArticles.ts
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export const useArticles = (filters?: ArticleFilters) => {
  return useQuery({
    queryKey: ["articles", filters],
    queryFn: () => apiClient.getArticles(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

**Factory Pattern (Scrapers)**

```python
# scrapers/factory.py
class ScraperFactory:
    _scrapers = {
        'reddit': RedditScraper,
        'hackernews': HackerNewsScraper,
        'devto': DevToScraper,
    }

    @classmethod
    def create_scraper(cls, source_type: str) -> BaseScraper:
        scraper_class = cls._scrapers.get(source_type)
        if not scraper_class:
            raise ValueError(f"Unknown scraper type: {source_type}")
        return scraper_class()
```

## Workflows de Développement

### Feature Development (feature par feature)

1. **Backend First**

   ```bash
   # Créer migration DB
   alembic revision --autogenerate -m "add_trends_table"
   alembic upgrade head

   # Créer model + schema
   # Créer service
   # Créer route API
   # Tester avec curl/Postman
   ```

2. **Frontend Second**

   ```bash
   # Créer types TypeScript
   # Créer hook TanStack Query
   # Créer composant UI
   # Intégrer dans page
   ```

3. **Power BI Last**
   ```bash
   # Créer vue SQL optimisée
   # Connecter Power BI à PostgreSQL
   # Créer visualisations
   # Publier + embed dans frontend
   ```

### Testing

**Backend (Pytest)**

```python
# tests/test_scrapers/test_reddit.py
import pytest
from app.scrapers.reddit import RedditScraper

@pytest.mark.asyncio
async def test_reddit_scraper():
    scraper = RedditScraper()
    keywords = ["python", "fastapi"]

    async with scraper:
        articles = await scraper.fetch_articles(keywords, max_results=10)

    assert len(articles) > 0
    assert all('title' in a for a in articles)
    assert all('url' in a for a in articles)
```

**Frontend (Vitest)**

```typescript
// components/__tests__/ArticleCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ArticleCard } from '../ArticleCard';

describe('ArticleCard', () => {
  it('renders article title', () => {
    const article = {
      id: '1',
      title: 'Test Article',
      url: 'https://example.com',
      score: 85,
      category: 'dev'
    };

    render(<ArticleCard article={article} />);
    expect(screen.getByText('Test Article')).toBeInTheDocument();
  });
});
```

## Commandes Utiles

### Infrastructure

```bash
# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f backend
docker-compose logs -f celery

# Rebuild après changement de dépendances
docker-compose up -d --build

# Stop & cleanup
docker-compose down -v
```

### Backend

```bash
# Installation
cd backend
poetry install

# Lancer en dev
poetry run uvicorn app.main:app --reload --port 8000

# Migrations DB
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"

# Lancer Celery worker
poetry run celery -A app.tasks.celery_app worker --loglevel=info

# Lancer Celery beat (scheduler)
poetry run celery -A app.tasks.celery_app beat --loglevel=info

# Tests
poetry run pytest
poetry run pytest --cov=app tests/

# Linting
poetry run ruff check .
poetry run ruff format .
```

### Frontend

```bash
# Installation
cd frontend
npm install

# Dev
npm run dev

# Build
npm run build
npm run start

# Tests
npm run test
npm run test:ui

# Linting
npm run lint
npm run format
```

### Database

```bash
# Se connecter à PostgreSQL
docker-compose exec postgres psql -U user -d techwatch

# Backup
docker-compose exec postgres pg_dump -U user techwatch > backup.sql

# Restore
docker-compose exec -T postgres psql -U user techwatch < backup.sql

# Voir les tables
\dt

# Voir une vue
SELECT * FROM vw_articles_daily_stats LIMIT 10;
```

## Métriques de Succès

### Techniques

- ✅ API Response time : <200ms (95th percentile)
- ✅ Scraping : 100+ articles/jour
- ✅ NLP Scoring : <2s par article
- ✅ Frontend First Load : <2s (Lighthouse)
- ✅ Zero downtime deployments

### Business

- ✅ Précision : >80% articles pertinents (score >50)
- ✅ Temps économisé : 90min/jour de veille manuelle
- ✅ Taux de lecture : >70% pour articles score >70
- ✅ Détection tendances : 3-5 jours avant mainstream

## Notes Spécifiques au Projet

### Power BI Embedded

**Configuration Token**

```typescript
// lib/powerbi-config.ts
import { models } from "powerbi-client";

export const getPowerBIConfig = (
  embedToken: string,
): models.IReportEmbedConfiguration => ({
  type: "report",
  tokenType: models.TokenType.Embed,
  accessToken: embedToken,
  embedUrl: process.env.NEXT_PUBLIC_POWERBI_EMBED_URL!,
  id: process.env.NEXT_PUBLIC_POWERBI_REPORT_ID!,
  settings: {
    panes: {
      filters: { expanded: false, visible: true },
    },
    background: models.BackgroundType.Transparent,
  },
});
```

### NLP Scoring Algorithm

Le scoring combine 3 approches :

1. **Exact Match** (40%) : Le mot-clé apparaît tel quel
2. **Semantic Similarity** (30%) : Similarité avec spaCy embeddings
3. **TF-IDF Cosine** (30%) : Importance du terme dans le document

Score final = moyenne pondérée × poids du mot-clé

### Celery Beat Schedule

```python
# tasks/celery_app.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'scrape-every-6-hours': {
        'task': 'app.tasks.scraping.scrape_all_sources',
        'schedule': crontab(hour='*/6'),  # Toutes les 6h
    },
    'send-daily-digest': {
        'task': 'app.tasks.email.send_daily_digest',
        'schedule': crontab(hour=8, minute=0),  # 8h00 chaque jour
    },
}
```

---

**Dernière mise à jour** : Décembre 2024
**Version** : 1.0.0
**Auteur** : Tom (Epitech Lyon)
