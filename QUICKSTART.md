# TechWatch - Guide de Démarrage Rapide

## 🚀 Démarrage Ultra-Rapide (Docker)

### Prérequis
- Docker 24+ et Docker Compose 2+
- 4GB RAM minimum
- Ports disponibles : 3000, 8000, 5432, 6379

### Lancement Complet (1 commande)

```bash
# Lancer TOUS les services (frontend, backend, DB, Redis, Celery)
docker-compose up -d

# Vérifier que tout tourne
docker-compose ps
```

**Services démarrés :**
- ✅ PostgreSQL (port 5433) - Ports modifiés pour éviter conflits
- ✅ Redis (port 6379)
- ✅ Backend FastAPI (port 8001)
- ✅ Celery Worker (scraping)
- ✅ Celery Beat (scheduler 6h)
- ✅ Frontend Next.js (port 3001)

### Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3001 | Dashboard Next.js |
| **Backend API** | http://localhost:8001 | FastAPI REST API |
| **API Docs** | http://localhost:8001/docs | Swagger UI interactive |
| **PostgreSQL** | localhost:5433 | Base de données |
| **Redis** | localhost:6379 | Cache & queue |

> **Note**: Les ports par défaut ont été modifiés (5433 au lieu de 5432, 8001 au lieu de 8000, 3001 au lieu de 3000) pour éviter les conflits avec d'éventuels services locaux.

### Premiers Tests

#### 1. Vérifier l'API Backend
```bash
# Health check
curl http://localhost:8001/health

# Lister les sources disponibles
curl http://localhost:8001/api/sources
```

#### 2. Déclencher un Scraping Manuel
```bash
curl -X POST http://localhost:8001/api/scraping/trigger \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["python", "AI", "blockchain"]}'

# Récupérer le task_id de la réponse et vérifier le statut
curl http://localhost:8001/api/scraping/status/{task_id}
```

#### 3. Accéder au Frontend
Ouvrir http://localhost:3001 dans votre navigateur.

### Arrêter les Services

```bash
# Arrêt propre
docker-compose down

# Arrêt + suppression des volumes (⚠️ perd les données)
docker-compose down -v
```

---

## 🔧 Développement Local (sans Docker)

### Backend (FastAPI)

#### Installation
```bash
cd backend

# Installer Poetry si nécessaire
curl -sSL https://install.python-poetry.org | python3 -

# Installer les dépendances
poetry install

# Télécharger les modèles spaCy
poetry run python -m spacy download en_core_web_lg
poetry run python -m spacy download fr_core_news_lg
```

#### Configuration Backend
```bash
# Utiliser le fichier .env local (SQLite)
cd backend
cp .env.example .env

# Éditer .env si besoin (API keys, etc.)
nano .env
```

#### Migrations Database
```bash
# Appliquer les migrations
poetry run alembic upgrade head

# Créer une nouvelle migration (si modifications de models)
poetry run alembic revision --autogenerate -m "description"
```

#### Seed Data (Sources initiales)
```bash
poetry run python -m app.scripts.seed_sources
```

#### Lancer le Backend
```bash
# Mode dev avec hot-reload
poetry run uvicorn app.main:app --reload --port 8000

# Avec log détaillé
poetry run uvicorn app.main:app --reload --port 8000 --log-level debug
```

#### Lancer Celery (dans des terminaux séparés)

**Terminal 1 - Worker:**
```bash
cd backend
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 2 - Beat (scheduler):**
```bash
cd backend
poetry run celery -A app.tasks.celery_app beat --loglevel=info
```

#### Tests Backend
```bash
# Tous les tests
poetry run pytest

# Avec coverage
poetry run pytest --cov=app tests/

# Test spécifique
poetry run pytest tests/test_scrapers/test_reddit_plugin.py

# Verbose
poetry run pytest -v -s
```

#### Linting & Formatting
```bash
# Check linting
poetry run ruff check .

# Auto-fix
poetry run ruff check --fix .

# Formatting
poetry run ruff format .
```

---

### Frontend (Next.js)

#### Installation
```bash
cd frontend

# Installer les dépendances
npm install

# Ou avec pnpm/yarn
pnpm install
```

#### Configuration Frontend
```bash
# Variables d'env (déjà dans .env root)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Lancer le Frontend
```bash
# Mode dev avec hot-reload
npm run dev

# Sur un port custom
npm run dev -- -p 3001
```

#### Build Production
```bash
# Build optimisé
npm run build

# Lancer en mode production
npm run start
```

#### Tests Frontend
```bash
# Lancer les tests
npm run test

# Mode watch
npm run test -- --watch

# UI interactive
npm run test:ui
```

#### Linting & Formatting
```bash
# ESLint
npm run lint

# Prettier
npm run format
```

---

## 📊 Database (PostgreSQL)

### Connexion Directe

```bash
# Via Docker
docker-compose exec postgres psql -U techwatch_user -d techwatch

# Local (si PostgreSQL installé)
psql -h localhost -U techwatch_user -d techwatch
```

### Commandes SQL Utiles

```sql
-- Lister les tables
\dt

-- Voir le schéma d'une table
\d+ articles

-- Compter les articles
SELECT COUNT(*) FROM articles;

-- Top 10 articles par score
SELECT title, score, category FROM articles
ORDER BY score DESC LIMIT 10;

-- Articles scrapés aujourd'hui
SELECT COUNT(*) FROM articles
WHERE scraped_at::date = CURRENT_DATE;

-- Voir les sources actives
SELECT name, type, last_scraped_at FROM sources
WHERE is_active = true;

-- Statistiques par catégorie
SELECT category, COUNT(*), AVG(score)
FROM articles
GROUP BY category;

-- Vue Power BI : stats quotidiennes
SELECT * FROM vw_articles_daily_stats
ORDER BY date DESC LIMIT 7;

-- Quitter
\q
```

### Backup & Restore

```bash
# Backup complet
docker-compose exec postgres pg_dump -U techwatch_user techwatch > backup_$(date +%Y%m%d).sql

# Backup via Docker sans exec
docker-compose exec -T postgres pg_dump -U techwatch_user techwatch > backup.sql

# Restore
docker-compose exec -T postgres psql -U techwatch_user techwatch < backup.sql

# Backup uniquement le schéma
docker-compose exec postgres pg_dump -U techwatch_user --schema-only techwatch > schema.sql

# Backup uniquement les données
docker-compose exec postgres pg_dump -U techwatch_user --data-only techwatch > data.sql
```

### Réinitialiser la DB

```bash
# ⚠️ ATTENTION : Supprime TOUTES les données
docker-compose down -v
docker-compose up -d postgres
# Les tables seront recréées via init.sql au démarrage
```

---

## 🔍 Logs & Debugging

### Logs Docker

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f frontend

# 100 dernières lignes
docker-compose logs --tail=100 backend

# Logs depuis une date
docker-compose logs --since 2024-01-01T10:00:00 backend
```

### Logs Backend (local)

```bash
# Logs dans la console (uvicorn)
poetry run uvicorn app.main:app --reload --log-level debug

# Logs Celery
poetry run celery -A app.tasks.celery_app worker --loglevel=debug
```

### Debugging

```bash
# Entrer dans un container
docker-compose exec backend /bin/bash
docker-compose exec postgres /bin/bash

# Inspecter les processus
docker-compose exec backend ps aux

# Vérifier les variables d'env
docker-compose exec backend env | grep DATABASE_URL
```

---

## 🛠️ Commandes Utiles

### Docker

```bash
# Rebuild après changement de dépendances
docker-compose up -d --build

# Rebuild un service spécifique
docker-compose up -d --build backend

# Voir l'usage des ressources
docker stats

# Nettoyer les images inutilisées
docker system prune -a

# Voir les volumes
docker volume ls

# Supprimer les volumes orphelins
docker volume prune
```

### Celery

```bash
# Voir les tasks actives
poetry run celery -A app.tasks.celery_app inspect active

# Voir les tasks registered
poetry run celery -A app.tasks.celery_app inspect registered

# Voir les workers connectés
poetry run celery -A app.tasks.celery_app inspect stats

# Purger toutes les tasks en queue
poetry run celery -A app.tasks.celery_app purge

# Flower (monitoring UI, si installé)
poetry run celery -A app.tasks.celery_app flower
```

### Redis

```bash
# Connexion Redis
docker-compose exec redis redis-cli

# Commandes Redis
PING
KEYS *
GET key_name
FLUSHALL  # ⚠️ Vide tout Redis
```

---

## 🔐 Configuration API Keys

### Anthropic (Claude) - Pour les résumés IA

1. Créer un compte : https://console.anthropic.com
2. Générer une API key
3. Ajouter dans `.env` :
```bash
ANTHROPIC_API_KEY=sk-ant-api03-votre-clé-ici
```

### Reddit - Pour scraper r/programming, etc.

1. Créer une app : https://www.reddit.com/prefs/apps
2. Choisir "script" type
3. Noter `client_id` et `client_secret`
4. Ajouter dans `.env` :
```bash
REDDIT_CLIENT_ID=votre_client_id
REDDIT_CLIENT_SECRET=votre_client_secret
REDDIT_USER_AGENT=TechWatch/1.0
```

### SMTP (Email Digest) - Optionnel

Pour Gmail avec App Password :
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-app-password
EMAIL_FROM=noreply@techwatch.local
```

---

## 🎯 Workflows de Développement

### Ajouter une Nouvelle Source de Scraping

1. Créer le plugin :
```bash
cd backend/app/scrapers/plugins
touch newsource.py
```

2. Implémenter le scraper (voir `SCRAPING_SYSTEM.md`)

3. Tester :
```bash
poetry run pytest tests/test_scrapers/test_newsource.py
```

4. Ajouter la source en DB :
```sql
INSERT INTO sources (name, type, base_url, config) VALUES
('NewSource', 'newsource', 'https://example.com', '{"max_articles": 50}');
```

### Ajouter un Endpoint API

1. Créer le schema :
```bash
cd backend/app/schemas
nano new_feature.py
```

2. Créer la route :
```bash
cd backend/app/api
nano new_feature.py
```

3. Tester :
```bash
curl -X POST http://localhost:8000/api/new_feature -H "Content-Type: application/json" -d '{}'
```

### Modifier la DB

1. Modifier le model :
```bash
nano backend/app/models/article.py
```

2. Générer la migration :
```bash
cd backend
poetry run alembic revision --autogenerate -m "add column xyz"
```

3. Appliquer :
```bash
poetry run alembic upgrade head
```

---

## ⚡ Métriques de Performance

### Objectifs

- **API Response** : < 200ms (P95)
- **Scraping** : 100+ articles/jour
- **NLP Scoring** : < 2s par article
- **Frontend Load** : < 2s (First Contentful Paint)

### Monitoring

```bash
# Backend response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/articles

# Scraping stats (dernières 24h)
docker-compose exec postgres psql -U techwatch_user -d techwatch -c \
  "SELECT COUNT(*) FROM articles WHERE scraped_at > NOW() - INTERVAL '24 hours';"

# Worker performance
docker stats techwatch_celery_worker
```

---

## 🐛 Troubleshooting

### Backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Problème de DB ? Vérifier PostgreSQL
docker-compose exec postgres pg_isready

# Problème de migrations ?
docker-compose exec backend poetry run alembic current
docker-compose exec backend poetry run alembic upgrade head
```

### Celery ne scrape pas

```bash
# Worker actif ?
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect active

# Redis OK ?
docker-compose exec redis redis-cli PING

# Vérifier les sources actives
docker-compose exec postgres psql -U techwatch_user -d techwatch -c \
  "SELECT name, is_active FROM sources;"
```

### Frontend erreur 500

```bash
# Backend accessible ?
curl http://localhost:8000/health

# CORS configuré ?
# Vérifier dans backend/app/main.py : allow_origins=["http://localhost:3000"]
```

### Aucun article scrapé

```bash
# Vérifier les keywords actifs
docker-compose exec postgres psql -U techwatch_user -d techwatch -c \
  "SELECT * FROM keywords WHERE is_active = true;"

# Déclencher manuellement
curl -X POST http://localhost:8000/api/scraping/trigger \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["python"]}'

# Voir les erreurs dans scraping_runs
docker-compose exec postgres psql -U techwatch_user -d techwatch -c \
  "SELECT * FROM scraping_runs ORDER BY started_at DESC LIMIT 5;"
```

---

## 📚 Documentation Complète

- **Architecture** : `.claude/CLAUDE.md`
- **Système de Scraping** : `backend/SCRAPING_SYSTEM.md`
- **API Reference** : http://localhost:8000/docs
- **README Principal** : `README.md`

---

## 🚦 Statut des Services (Checklist)

Après `docker-compose up -d`, vérifier :

- [ ] PostgreSQL : `docker-compose exec postgres pg_isready`
- [ ] Redis : `docker-compose exec redis redis-cli PING`
- [ ] Backend : `curl http://localhost:8000/health`
- [ ] Frontend : Ouvrir http://localhost:3000
- [ ] Celery Worker : `docker-compose logs celery_worker | grep "ready"`
- [ ] Celery Beat : `docker-compose logs celery_beat | grep "beat"`

**Tout est OK ?** ✅ Vous êtes prêt à développer !

---

**Dernière mise à jour** : 2024-12-31
**Version** : 1.0.0
