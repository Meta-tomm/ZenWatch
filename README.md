# TechWatch - Plateforme de Veille Technologique Intelligente

Plateforme automatisée de veille technologique qui collecte, analyse et présente des articles pertinents depuis Reddit, HackerNews, Dev.to, Medium et GitHub Trending.

## Stack Technique

- **Backend**: Python 3.11+ / FastAPI / SQLAlchemy / Celery
- **Frontend**: Next.js 14 / TypeScript / TailwindCSS / shadcn/ui
- **Database**: PostgreSQL 16 / Redis 7
- **AI**: Anthropic Claude API (résumés) / spaCy (NLP scoring)
- **BI**: Power BI Desktop / Power BI Embedded
- **Infra**: Docker / Docker Compose

## Architecture

```
techwatch/
├── backend/         # API FastAPI + Scrapers + NLP
├── frontend/        # Dashboard Next.js
├── database/        # Scripts SQL + vues Power BI
├── infra/           # Docker configs
└── powerbi/         # Fichiers Power BI
```

## Installation

### Prérequis

- Docker & Docker Compose
- Python 3.11+ (pour dev local)
- Node.js 18+ (pour dev local)
- Clé API Anthropic (Claude)

### Configuration

1. Cloner le repository:
```bash
git clone <repo-url>
cd ZenWatch
```

2. Copier et configurer les variables d'environnement:
```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

3. Lancer les services:
```bash
docker-compose up -d
```

4. Accéder aux services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Développement

### Backend (FastAPI)

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# Migrations DB
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"

# Tests
poetry run pytest
poetry run pytest --cov=app

# Linting
poetry run ruff check .
poetry run ruff format .
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev

# Tests
npm run test
npm run test:ui

# Build
npm run build
```

### Celery (Workers)

```bash
# Worker
poetry run celery -A app.tasks.celery_app worker --loglevel=info

# Beat (scheduler)
poetry run celery -A app.tasks.celery_app beat --loglevel=info
```

## Fonctionnalités

- Scraping automatique multi-sources (Reddit, HN, Dev.to, GitHub, Medium)
- Scoring NLP avec spaCy + TF-IDF (pertinence 0-100)
- Résumés IA générés via Claude API
- Dashboard interactif avec filtres et recherche
- Gestion mots-clés personnalisables avec poids
- Détection de tendances automatique
- Email digest quotidien
- Dashboards Power BI intégrés

## Commandes Utiles

### Docker

```bash
# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Rebuild
docker-compose up -d --build

# Stop & cleanup
docker-compose down -v
```

### Database

```bash
# Se connecter à PostgreSQL
docker-compose exec postgres psql -U techwatch_user -d techwatch

# Backup
docker-compose exec postgres pg_dump -U techwatch_user techwatch > backup.sql

# Restore
docker-compose exec -T postgres psql -U techwatch_user techwatch < backup.sql
```

## Configuration API Keys

### Anthropic (Claude)

1. Créer un compte sur https://console.anthropic.com
2. Générer une API key
3. Ajouter dans `.env`: `ANTHROPIC_API_KEY=sk-ant-xxx`

### Reddit

1. Créer une app sur https://www.reddit.com/prefs/apps
2. Récupérer client_id et client_secret
3. Ajouter dans `.env`:
```
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
REDDIT_USER_AGENT=TechWatch/1.0
```

## Workflow de Développement

1. Backend First: Migration DB → Model → Schema → Service → Route API
2. Frontend Second: Types TS → Hook TanStack Query → Composant UI
3. Power BI Last: Vue SQL → Dashboard → Embed

## Métriques de Succès

- API Response time: <200ms (P95)
- Scraping: 100+ articles/jour
- NLP Scoring: <2s par article
- Frontend First Load: <2s
- Précision: >80% articles pertinents (score >50)

## Documentation

- [Architecture détaillée](.claude/CLAUDE.md)
- [API Docs](http://localhost:8000/docs)
- [Schéma DB](database/schema.md)

## Licence

MIT

## Auteur

Tom (Epitech Lyon)
