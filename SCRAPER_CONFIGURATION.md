# Configuration Manuelle des Scrapers - TechWatch

Ce guide explique comment obtenir et configurer les API keys pour chaque source de scraping.

## Table des Matières

1. [Reddit](#1-reddit)
2. [HackerNews](#2-hackernews)
3. [Dev.to](#3-devto)
4. [GitHub Trending](#4-github-trending)
5. [Medium](#5-medium)
6. [Configuration .env](#configuration-env)
7. [Test des Scrapers](#test-des-scrapers)

---

## 1. Reddit

### Obtenir les clés API Reddit

1. **Créer une application Reddit**:
   - Aller sur https://www.reddit.com/prefs/apps
   - Cliquer sur "Create App" ou "Create Another App"
   - Remplir le formulaire:
     - **name**: `TechWatch Scraper`
     - **App type**: Sélectionner "script"
     - **description**: `Article scraping for tech news`
     - **about url**: Laisser vide
     - **redirect uri**: `http://localhost:8000`
   - Cliquer sur "Create app"

2. **Récupérer les credentials**:
   - **CLIENT_ID**: La chaîne sous "personal use script" (14 caractères)
   - **CLIENT_SECRET**: La chaîne à côté de "secret" (27 caractères)
   - **USER_AGENT**: Format: `platform:app_name:version (by u/your_username)`
     - Exemple: `linux:techwatch:v1.0.0 (by u/your_reddit_username)`

3. **Ajouter au .env**:
```env
REDDIT_CLIENT_ID=votre_client_id_ici
REDDIT_CLIENT_SECRET=votre_client_secret_ici
REDDIT_USER_AGENT=linux:techwatch:v1.0.0 (by u/votre_username)
```

### Subreddits recommandés pour la tech

Par défaut, le scraper utilise ces subreddits:
- `r/programming` - Actualités programmation générale
- `r/webdev` - Développement web
- `r/MachineLearning` - IA et ML
- `r/technology` - Tech générale
- `r/datascience` - Data science
- `r/devops` - DevOps et infra
- `r/golang` - Go programming
- `r/rust` - Rust programming

**Modifier la liste**: Dans `/backend/app/scrapers/plugins/reddit.py`, ligne ~50.

---

## 2. HackerNews

### Configuration

**Bonne nouvelle**: HackerNews ne nécessite PAS d'API key!

L'API HackerNews est publique et accessible via Firebase:
- API officielle: https://github.com/HackerNews/API
- Endpoint: `https://hacker-news.firebaseio.com/v0/`

**Aucune configuration nécessaire** - Le scraper fonctionne directement.

### Points de scraping

Le scraper récupère automatiquement:
- **Top Stories**: Articles les plus votés
- **New Stories**: Derniers articles
- **Best Stories**: Meilleurs articles (algorithme HN)

**Rate Limiting**: L'API HackerNews n'a pas de limite stricte, mais il est recommandé de ne pas faire plus de 1 requête/seconde.

---

## 3. Dev.to

### Obtenir l'API key Dev.to

1. **Créer un compte Dev.to**:
   - Aller sur https://dev.to
   - Créer un compte si vous n'en avez pas

2. **Générer une API key**:
   - Aller sur https://dev.to/settings/extensions
   - Descendre jusqu'à "DEV Community API Keys"
   - Cliquer sur "Generate API Key"
   - **Description**: `TechWatch Scraper`
   - Copier la clé générée (commence par un long string)

3. **Ajouter au .env**:
```env
DEVTO_API_KEY=votre_api_key_dev_to_ici
```

### Tags recommandés

Par défaut, le scraper récupère les articles avec ces tags:
- `javascript`
- `python`
- `webdev`
- `programming`
- `devops`
- `ai`
- `beginners`

**Modifier les tags**: Dans `/backend/app/scrapers/plugins/devto.py`.

---

## 4. GitHub Trending

### Configuration

**Bonne nouvelle**: GitHub Trending ne nécessite PAS d'API key pour le scraping basique!

Cependant, pour éviter le rate limiting, vous pouvez ajouter un **Personal Access Token** (optionnel mais recommandé).

### Obtenir un GitHub Token (Optionnel)

1. **Créer un token**:
   - Aller sur https://github.com/settings/tokens
   - Cliquer sur "Generate new token" → "Generate new token (classic)"
   - **Note**: `TechWatch Scraper`
   - **Scopes**: Ne sélectionner AUCUN scope (lecture publique uniquement)
   - Cliquer sur "Generate token"
   - Copier le token (commence par `ghp_`)

2. **Ajouter au .env** (optionnel):
```env
GITHUB_TOKEN=ghp_votre_token_ici
```

### Langages et périodes

Le scraper GitHub Trending peut filtrer par:
- **Langages**: `python`, `javascript`, `rust`, `go`, `typescript`, etc.
- **Période**: `daily`, `weekly`, `monthly`

**Configuration actuelle**: Dans `/backend/app/scrapers/plugins/github.py`.

---

## 5. Medium

### Configuration

Medium peut être scrapé de deux façons:

#### Option A: RSS Feed (Recommandé - Pas de clé nécessaire)

Utilise les flux RSS publics de Medium:
- `https://medium.com/feed/tag/programming`
- `https://medium.com/feed/tag/technology`
- `https://medium.com/feed/tag/data-science`

**Aucune configuration nécessaire**.

#### Option B: Medium API (Optionnel)

Si vous voulez plus de contrôle:

1. **Créer une application Medium**:
   - Aller sur https://medium.com/me/applications
   - Cliquer sur "New Application"
   - Remplir les informations

2. **Récupérer le token**:
   - Une fois créé, copier l'**Integration Token**

3. **Ajouter au .env**:
```env
MEDIUM_API_TOKEN=votre_token_medium_ici
```

**Note**: L'API Medium officielle est très limitée. Le RSS est suffisant pour la plupart des cas.

---

## Configuration .env

### Fichier .env complet

Créer/modifier le fichier `/backend/.env`:

```env
# Database
DATABASE_URL=postgresql://techwatch_user:techwatch_password@postgres:5432/techwatch
POSTGRES_USER=techwatch_user
POSTGRES_PASSWORD=techwatch_password
POSTGRES_DB=techwatch

# Redis
REDIS_URL=redis://redis:6379/0

# Claude AI (pour les résumés)
ANTHROPIC_API_KEY=sk-ant-votre_cle_anthropic_ici

# Reddit
REDDIT_CLIENT_ID=votre_client_id_reddit
REDDIT_CLIENT_SECRET=votre_client_secret_reddit
REDDIT_USER_AGENT=linux:techwatch:v1.0.0 (by u/votre_username)

# Dev.to
DEVTO_API_KEY=votre_api_key_devto

# GitHub (optionnel)
GITHUB_TOKEN=ghp_votre_token_github

# Medium (optionnel)
MEDIUM_API_TOKEN=votre_token_medium

# Application
SECRET_KEY=votre_secret_key_pour_jwt_ici
DEBUG=True
```

### Obtenir une clé Anthropic (pour les résumés IA)

1. Aller sur https://console.anthropic.com/
2. Créer un compte
3. Aller dans "API Keys"
4. Créer une nouvelle clé
5. Copier la clé (commence par `sk-ant-`)

**Important**: Sans cette clé, les résumés IA ne seront pas générés, mais le reste du système fonctionne.

---

## Test des Scrapers

### 1. Redémarrer les services après configuration

```bash
cd /home/chapuis/Documents/ZenWatch
docker-compose down
docker-compose up -d
```

### 2. Tester Reddit

```bash
# Déclencher manuellement le scraping Reddit
docker-compose exec celery_worker celery -A app.tasks.celery_app call scrape_all_sources --args='[["python", "AI"]]'

# Vérifier les logs
docker-compose logs celery_worker --tail 50 | grep -i reddit
```

### 3. Vérifier les articles scrapés

```bash
# Voir le nombre d'articles
docker-compose exec postgres psql -U techwatch_user -d techwatch -c "SELECT COUNT(*) FROM articles;"

# Voir les 5 derniers articles
docker-compose exec postgres psql -U techwatch_user -d techwatch -c "
SELECT id, title, score, category, source_id
FROM articles
ORDER BY created_at DESC
LIMIT 5;
"
```

### 4. Tester via l'API

```bash
# Health check
curl http://localhost:8000/health

# Voir les articles
curl http://localhost:8000/api/articles?limit=10 | jq

# Voir les analytics
curl http://localhost:8000/api/analytics/summary | jq
```

### 5. Déclencher manuellement chaque scraper

```bash
# Scraper Reddit uniquement
docker-compose exec backend python -c "
from app.scrapers.plugins.reddit import RedditScraper
import asyncio

async def test():
    scraper = RedditScraper()
    articles = await scraper.fetch_articles(['python', 'AI'], max_results=10)
    print(f'Scraped {len(articles)} articles')
    for article in articles[:3]:
        print(f'- {article[\"title\"]}')

asyncio.run(test())
"
```

---

## Dépannage

### Erreur: "Invalid credentials" (Reddit)

- Vérifier que `REDDIT_CLIENT_ID` et `REDDIT_CLIENT_SECRET` sont corrects
- Vérifier que l'app Reddit est bien de type "script"
- Vérifier que le `.env` est bien dans `/backend/`

### Erreur: "Rate limit exceeded"

- Attendre quelques minutes
- Pour Reddit: Vérifier le `USER_AGENT` (doit être unique)
- Pour GitHub: Ajouter un `GITHUB_TOKEN`

### Aucun article scrapé

1. **Vérifier les logs**:
```bash
docker-compose logs celery_worker --tail 100
```

2. **Vérifier les sources actives**:
```bash
docker-compose exec postgres psql -U techwatch_user -d techwatch -c "
SELECT name, type, is_active, last_scraped_at
FROM sources;
"
```

3. **Activer une source**:
```bash
docker-compose exec postgres psql -U techwatch_user -d techwatch -c "
UPDATE sources SET is_active = true WHERE type = 'reddit';
"
```

### Les résumés IA ne sont pas générés

- Vérifier que `ANTHROPIC_API_KEY` est configuré
- Vérifier les crédits sur https://console.anthropic.com/
- Les résumés sont générés par la tâche `summarize_articles` (exécutée quotidiennement à 9h)

---

## Monitoring

### Voir les tâches Celery en cours

```bash
# Voir les tâches actives
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect active

# Voir les tâches planifiées
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect scheduled
```

### Voir les statistiques

```bash
# Nombre d'articles par source
docker-compose exec postgres psql -U techwatch_user -d techwatch -c "
SELECT s.name, COUNT(a.id) as article_count
FROM sources s
LEFT JOIN articles a ON a.source_id = s.id
GROUP BY s.name
ORDER BY article_count DESC;
"

# Top keywords avec le plus d'articles
docker-compose exec postgres psql -U techwatch_user -d techwatch -c "
SELECT k.keyword, COUNT(ak.article_id) as article_count
FROM keywords k
LEFT JOIN article_keywords ak ON ak.keyword_id = k.id
GROUP BY k.keyword
ORDER BY article_count DESC
LIMIT 10;
"
```

---

## Planification Automatique

Les scrapers s'exécutent automatiquement selon ce planning (défini dans `celery_app.py`):

- **Scraping**: Toutes les 6h (00:00, 06:00, 12:00, 18:00) + quotidien à 08:00
- **Scoring NLP**: Toutes les heures à :15
- **Résumés IA**: Quotidien à 09:00
- **Détection trends**: Quotidien à 10:00
- **Nettoyage**: Dimanche à 03:00

### Modifier la planification

Éditer `/backend/app/tasks/celery_app.py` section `beat_schedule`.

Puis redémarrer:
```bash
docker-compose restart celery_beat
```

---

## Ressources Utiles

- **Reddit API**: https://www.reddit.com/dev/api/
- **HackerNews API**: https://github.com/HackerNews/API
- **Dev.to API**: https://developers.forem.com/api
- **GitHub API**: https://docs.github.com/en/rest
- **Anthropic Claude**: https://docs.anthropic.com/

---

**Dernière mise à jour**: 2 janvier 2026
**Auteur**: Configuration TechWatch
