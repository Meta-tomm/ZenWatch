# Design du Système de Scraping - TechWatch

**Date**: 2025-12-29
**Version**: 1.0.0
**Auteur**: Tom (Epitech Lyon)
**Status**: Validé

## Vue d'ensemble

Système de scraping multi-sources pour la plateforme TechWatch, capable de collecter automatiquement des articles depuis Reddit, HackerNews, Dev.to, GitHub Trending et Medium. Le système utilise une architecture plugin scalable, un scraping intelligent avec filtrage par mots-clés, et supporte l'exécution schedulée (Celery) et on-demand (API).

## Objectifs

- **Scalabilité**: Ajouter facilement de nouvelles sources sans refactoring
- **Performance**: Scraping semi-parallèle, filtrage intelligent pour économiser les ressources
- **Fiabilité**: Gestion robuste des erreurs, respect des rate limits, retry avec backoff
- **Flexibilité**: Configuration par source, triggers multiples (scheduled + on-demand)

## Décisions de Design

### Sources à Implémenter

Toutes les sources dès le début (approche comprehensive):
- **Reddit** (API OAuth2)
- **HackerNews** (Firebase API)
- **Dev.to** (API REST)
- **GitHub Trending** (scraping HTML)
- **Medium** (RSS feeds)

### Triggers de Scraping

**Hybride - Scheduled ET On-Demand**:
- Celery Beat pour scraping automatique (toutes les 6h)
- API endpoint pour déclenchement manuel
- Logique partagée pour les deux modes

### Extraction de Données

**Smart extraction**:
1. Premier pass: champs essentiels uniquement (title, url, published_at)
2. Quick keyword match sur le titre
3. Si pertinent: fetch rich metadata (content, author, upvotes, tags, etc.)

**Bénéfice**: Économie de bande passante et d'API calls

### Quantité d'Articles

**Configurable par source**:
- Reddit: 100 articles
- HackerNews: 50 articles
- Dev.to: 50 articles
- GitHub Trending: 25 repos
- Medium: 30 articles

Stocké en DB (table `sources`, colonne `config` JSONB)

### Gestion Rate Limits et Erreurs

**Approche intelligente**:
- Token bucket algorithm pour respecter les rate limits
- Retry avec backoff exponentiel (3 tentatives max)
- Mise en queue Redis des échecs pour réessai ultérieur
- Logging détaillé de chaque étape

### Déduplication

**Après scraping**:
- Pas de déduplication pendant le scraping (garde simplicité)
- Module NLP deduplicator traite les doublons après coup
- Permet détection de similarité sémantique plus sophistiquée

### Exécution des Scrapers

**Semi-parallèle**:
- Groupes de 2-3 scrapers en parallèle via `asyncio.gather`
- Compromis performance/ressources
- Évite surcharge CPU/réseau

### Gestion Articles Existants

**Update metadata**:
- Si URL existe en DB: UPDATE upvotes, comments_count, tags
- Sinon: INSERT nouveau
- Garde les données fraîches (métriques sociales évoluent)

### Validation Données

**Approche hybride**:
- Champs obligatoires: `title`, `url` (rejet si manquants)
- Champs optionnels: `author`, `content`, `tags`, etc. (peuvent être NULL)
- Validation via Pydantic schemas

### Configuration

**Hybride - Secrets en .env + Config en DB**:
- **Secrets** (API keys): variables d'environnement `.env`
- **Config fonctionnelle**: table `sources`, colonne `config` JSONB
- Flexibilité + sécurité

## Architecture Technique

### Pattern: Plugin Architecture

Choix pour scalabilité maximale. Ajouter une source = créer un fichier plugin, auto-découvert par le registry.

```
backend/app/scrapers/
├── __init__.py           # Plugin registry
├── base.py               # ScraperPlugin interface
├── registry.py           # Auto-découverte
├── plugins/
│   ├── reddit.py         # @scraper_plugin
│   ├── hackernews.py     # @scraper_plugin
│   ├── devto.py          # @scraper_plugin
│   ├── github.py         # @scraper_plugin
│   └── medium.py         # @scraper_plugin
└── strategies/
    ├── auth.py           # OAuth2Strategy, APIKeyStrategy
    ├── rate_limit.py     # RateLimiter (token bucket)
    └── retry.py          # RetryStrategy (backoff exponentiel)
```

### Interface ScraperPlugin

```python
class ScraperPlugin(ABC):
    # Métadonnées
    name: str
    display_name: str
    version: str

    @abstractmethod
    async def scrape(self, config: dict, keywords: List[str]) -> List[ArticleData]:
        """Point d'entrée unique du plugin"""
        pass

    @abstractmethod
    def validate_config(self, config: dict) -> bool:
        """Valide la config spécifique au plugin"""
        pass
```

### Auto-registration

```python
@scraper_plugin(
    name="reddit",
    display_name="Reddit",
    version="1.0.0",
    required_config=["client_id", "client_secret", "subreddits"]
)
class RedditScraper(ScraperPlugin):
    async def scrape(self, config, keywords):
        # Implémentation spécifique
        pass
```

### Registry Dynamique

```python
# Découverte automatique au démarrage
registry = ScraperRegistry()
registry.discover_plugins()  # Scan plugins/

# Utilisation
scraper = registry.get("reddit")
articles = await scraper.scrape(config, keywords)
```

## Flow d'Exécution

### 1. Orchestration Principale

**Tâche Celery** `scrape_all_sources`:

```python
@celery_app.task(name="scrape_all_sources")
async def scrape_all_sources(keywords: List[str] = None):
    # 1. Récupérer sources actives depuis DB
    active_sources = db.query(Source).filter(Source.is_active == True).all()

    # 2. Charger keywords si non fournis
    if not keywords:
        keywords = [kw.keyword for kw in db.query(Keyword).filter(Keyword.is_active == True).all()]

    # 3. Grouper en batches de 2-3
    batches = chunk_list(active_sources, batch_size=3)

    # 4. Exécuter batch par batch
    for batch in batches:
        tasks = [scrape_single_source(s.type, s.config, keywords) for s in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 2. Scraping d'une Source

```python
async def scrape_single_source(source_type: str, config: dict, keywords: List[str]):
    # 1. Récupérer plugin
    scraper = registry.get(source_type)

    # 2. Initialiser strategies
    rate_limiter = RateLimiter(config.get('rate_limit', 60))
    retry_strategy = RetryStrategy(max_retries=3, backoff_factor=2)

    # 3. Scraper avec gestion d'erreurs
    try:
        async with rate_limiter:
            articles = await retry_strategy.execute(scraper.scrape(config, keywords))

        # 4. Sauvegarder en DB
        saved_count = await save_articles(articles, source_type)

        # 5. Update timestamp
        await update_source_timestamp(source_type)

        return {"source": source_type, "scraped": len(articles), "saved": saved_count}

    except MaxRetriesExceeded as e:
        await queue_failed_scraping(source_type, config, keywords, error=str(e))
        logger.error(f"Failed to scrape {source_type}: {e}")
        return {"source": source_type, "error": str(e)}
```

### 3. Scraping Intelligent (dans chaque plugin)

```python
async def scrape(self, config: dict, keywords: List[str]) -> List[ArticleData]:
    limit = config.get('max_articles', 50)

    # 1. Premier pass: données essentielles (rapide)
    lightweight_articles = await self._fetch_lightweight(limit * 2)

    # 2. Quick keyword match
    relevant_articles = []
    for article in lightweight_articles:
        if await self._quick_match(article['title'], keywords):
            # 3. Fetch rich metadata si pertinent
            enriched = await self._fetch_rich_metadata(article['url'])
            relevant_articles.append(enriched)

            if len(relevant_articles) >= limit:
                break

    return relevant_articles
```

### 4. Sauvegarde en DB

```python
async def save_articles(articles: List[dict], source_type: str) -> int:
    saved_count = 0

    for article_data in articles:
        # Validation Pydantic
        try:
            validated = ArticleCreate(**article_data)
        except ValidationError:
            continue

        # Check doublon (par URL)
        existing = db.query(Article).filter(Article.url == validated.url).first()

        if existing:
            # UPDATE metadata
            existing.upvotes = validated.upvotes
            existing.comments_count = validated.comments_count
            existing.tags = validated.tags
            existing.updated_at = datetime.utcnow()
        else:
            # INSERT nouveau
            article = Article(**validated.dict(), source_type=source_type)
            db.add(article)
            saved_count += 1

        db.commit()

    return saved_count
```

## Triggers

### API Endpoint (On-Demand)

```python
@router.post("/scraping/trigger")
async def trigger_scraping(
    sources: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None
):
    task = scrape_all_sources.delay(sources=sources, keywords=keywords)

    return {
        "message": "Scraping started",
        "task_id": task.id,
        "status_url": f"/scraping/status/{task.id}"
    }

@router.get("/scraping/status/{task_id}")
async def get_scraping_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task.state,
        "result": task.result if task.ready() else None
    }
```

### Celery Beat (Scheduled)

```python
app.conf.beat_schedule = {
    'scrape-all-sources-every-6h': {
        'task': 'scrape_all_sources',
        'schedule': crontab(hour='*/6'),
        'kwargs': {'sources': None, 'keywords': None}
    }
}
```

## Strategies Réutilisables

### RateLimiter (Token Bucket)

```python
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.rate = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        async with self.lock:
            await self._wait_for_token()
            self.tokens -= 1

    def _refill_tokens(self):
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.rate, self.tokens + (elapsed * self.rate / 60))
        self.last_update = now
```

### RetryStrategy (Backoff Exponentiel)

```python
class RetryStrategy:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def execute(self, coro):
        for attempt in range(self.max_retries):
            try:
                return await coro
            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                if attempt < self.max_retries - 1:
                    wait_time = (self.backoff_factor ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(wait_time)

        raise MaxRetriesExceeded(f"Failed after {self.max_retries} retries")
```

## Exemple: Plugin Reddit

Démontre tous les concepts (OAuth2, rate limiting, smart extraction):

```python
@scraper_plugin(
    name="reddit",
    display_name="Reddit",
    version="1.0.0",
    required_config=["client_id", "client_secret", "subreddits"]
)
class RedditScraper(ScraperPlugin):

    def __init__(self):
        self.auth_strategy = OAuth2Strategy()
        self.rate_limiter = RateLimiter(requests_per_minute=60)
        self.base_url = "https://oauth.reddit.com"

    async def scrape(self, config: dict, keywords: List[str]) -> List[dict]:
        # 1. Auth OAuth2
        token = await self._get_access_token(config['client_id'], config['client_secret'])

        # 2. Fetch depuis subreddits
        all_articles = []
        for subreddit in config['subreddits']:
            posts = await self._fetch_subreddit_posts(subreddit, token, limit=config['max_articles'] * 2)

            # 3. Filter + enrich
            for post in posts:
                if self._quick_match(post['title'], keywords):
                    enriched = await self._enrich_post(post, token)
                    all_articles.append(enriched)

                    if len(all_articles) >= config['max_articles']:
                        break

        return all_articles

    async def _fetch_subreddit_posts(self, subreddit: str, token: str, limit: int):
        async with self.rate_limiter:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/r/{subreddit}/hot",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"limit": limit}
                )
                # Parse et retourne lightweight data

    async def _enrich_post(self, post: dict, token: str):
        async with self.rate_limiter:
            # Fetch rich metadata (selftext, author, tags)
            pass
```

## Configuration en Base de Données

### Table `sources`

```sql
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50),           -- 'reddit', 'hackernews', etc.
    base_url TEXT,
    is_active BOOLEAN DEFAULT true,
    scrape_frequency_hours INTEGER DEFAULT 6,
    last_scraped_at TIMESTAMP,
    config JSONB,               -- Config spécifique par source
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Exemple de configuration JSONB

```sql
-- Reddit
INSERT INTO sources (name, type, config) VALUES (
    'Reddit',
    'reddit',
    '{
        "client_id": "env:REDDIT_CLIENT_ID",
        "client_secret": "env:REDDIT_CLIENT_SECRET",
        "subreddits": ["programming", "python", "technology"],
        "max_articles": 100,
        "rate_limit": 60
    }'::jsonb
);

-- HackerNews
INSERT INTO sources (name, type, config) VALUES (
    'HackerNews',
    'hackernews',
    '{
        "max_articles": 50,
        "story_type": "top",
        "rate_limit": 120
    }'::jsonb
);
```

**Note**: `"env:VAR_NAME"` indique de récupérer la valeur depuis les variables d'environnement (sécurité des secrets).

## Validation avec Pydantic

### Schema ArticleCreate

```python
class ArticleCreate(BaseModel):
    # Champs obligatoires
    title: str = Field(..., min_length=1, max_length=500)
    url: str = Field(..., pattern=r'^https?://')
    published_at: datetime

    # Champs optionnels
    content: Optional[str] = Field(None, max_length=50000)
    author: Optional[str] = None
    upvotes: Optional[int] = 0
    comments_count: Optional[int] = 0
    tags: Optional[List[str]] = []
    language: Optional[str] = 'en'
    read_time_minutes: Optional[int] = None
```

## Monitoring et Métriques

### Table `scraping_runs`

Pour tracking des exécutions:

```sql
CREATE TABLE scraping_runs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE,
    source_type VARCHAR(50),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20),         -- 'success', 'failed', 'partial'
    articles_scraped INTEGER DEFAULT 0,
    articles_saved INTEGER DEFAULT 0,
    error_message TEXT
);
```

### Logging

Niveaux de log par étape:
- **INFO**: Début/fin scraping, nb articles scrapés/sauvés
- **WARNING**: Retry après échec, article invalide skippé
- **ERROR**: Échec après max retries, erreur validation critique

## Points d'Attention

### Sécurité

1. **Secrets**: JAMAIS en dur dans `config` JSONB, utiliser notation `"env:VAR_NAME"`
2. **SQL Injection**: Toujours utiliser SQLAlchemy ORM (queries paramétrées)
3. **Validation**: Valider TOUS les inputs avec Pydantic
4. **Rate limiting**: Respecter les ToS des APIs

### Performance

1. **Timeouts**: httpx timeout à 30s pour éviter hang
2. **Memory**: Limiter batch size si gros volumes
3. **DB connections**: Pool de connexions SQLAlchemy (max 20)
4. **Celery workers**: 4-8 workers selon CPU disponibles

### Rate Limits par Source

- **Reddit**: 60 requêtes/minute (avec OAuth2)
- **HackerNews**: Pas de limite stricte, mais respecter 120 req/min
- **Dev.to**: 1000 requêtes/heure
- **GitHub**: 60 requêtes/heure (sans auth), 5000/heure (avec token)
- **Medium**: RSS, pas de limite stricte

## Tests

### Tests Unitaires

- Chaque plugin individuellement (mock httpx)
- Strategies (RateLimiter, RetryStrategy)
- Validation Pydantic schemas
- Quick keyword match

### Tests d'Intégration

- Flow complet scraping → save DB
- Gestion doublons (insert vs update)
- Celery task execution

### Tests avec Fixtures

```python
@pytest.fixture
def mock_reddit_response():
    return {
        "data": {
            "children": [
                {"data": {"title": "Test", "url": "https://example.com", ...}}
            ]
        }
    }

@pytest.mark.asyncio
async def test_reddit_scraper(mock_reddit_response):
    scraper = RedditScraper()
    # Mock httpx calls
    # Assert results
```

## Prochaines Étapes

1. Implémenter base classes (`ScraperPlugin`, `ScraperRegistry`)
2. Implémenter strategies réutilisables (`RateLimiter`, `RetryStrategy`)
3. Implémenter plugin Reddit (le plus complexe)
4. Implémenter plugins HackerNews, Dev.to, GitHub, Medium
5. Créer tâche Celery `scrape_all_sources`
6. Créer API endpoints (`POST /scraping/trigger`, `GET /scraping/status/{id}`)
7. Configurer Celery Beat schedule
8. Tests unitaires et d'intégration
9. Documentation API (OpenAPI/Swagger)

## Métriques de Succès

- **Coverage**: >85% pour scrapers et strategies
- **Performance**: Scraping complet de 5 sources en <5 minutes
- **Fiabilité**: Taux d'échec <5% sur 1 semaine
- **Scalabilité**: Ajout d'une nouvelle source en <2h de dev

## Conclusion

Architecture plugin scalable et robuste, prête pour implémentation. Le design privilégie la flexibilité (facile d'ajouter des sources) et la fiabilité (gestion d'erreurs solide) tout en gardant une complexité raisonnable.
