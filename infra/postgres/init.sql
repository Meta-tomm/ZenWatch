-- TechWatch - Script d'initialisation PostgreSQL
-- Tables principales pour la plateforme de veille technologique

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: sources
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    base_url TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    scrape_frequency_hours INTEGER DEFAULT 6,
    last_scraped_at TIMESTAMP,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: keywords
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(100),
    weight FLOAT DEFAULT 1.0 CHECK (weight >= 1.0 AND weight <= 5.0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: articles
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
    external_id VARCHAR(500),
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    content TEXT,
    summary TEXT,
    author VARCHAR(200),
    published_at TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score FLOAT DEFAULT 0.0 CHECK (score >= 0.0 AND score <= 100.0),
    category VARCHAR(100),
    tags TEXT[],
    language VARCHAR(10) DEFAULT 'en',
    read_time_minutes INTEGER,
    upvotes INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    is_read BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, external_id)
);

-- Table: article_keywords (relation N:N)
CREATE TABLE IF NOT EXISTS article_keywords (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(article_id, keyword_id)
);

-- Table: trends
CREATE TABLE IF NOT EXISTS trends (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    trend_score FLOAT DEFAULT 0.0,
    article_count INTEGER DEFAULT 0,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keyword, date)
);

-- Table: user_config
CREATE TABLE IF NOT EXISTS user_config (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    daily_digest_enabled BOOLEAN DEFAULT TRUE,
    digest_time TIME DEFAULT '08:00:00',
    min_score_threshold FLOAT DEFAULT 50.0,
    preferred_categories TEXT[],
    email_frequency VARCHAR(20) DEFAULT 'daily',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index sur colonnes fréquemment filtrées
CREATE INDEX IF NOT EXISTS idx_articles_score ON articles(score DESC);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_is_archived ON articles(is_archived);
CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles(source_id);
CREATE INDEX IF NOT EXISTS idx_trends_date ON trends(date DESC);
CREATE INDEX IF NOT EXISTS idx_trends_keyword ON trends(keyword);

-- Trigger pour updated_at automatique
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_keywords_updated_at BEFORE UPDATE ON keywords
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_config_updated_at BEFORE UPDATE ON user_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Vue: articles_daily_stats (pour Power BI)
CREATE OR REPLACE VIEW vw_articles_daily_stats AS
SELECT
    DATE(published_at) as date,
    category,
    COUNT(*) as article_count,
    AVG(score) as avg_score,
    SUM(CASE WHEN is_read THEN 1 ELSE 0 END) as read_count,
    SUM(CASE WHEN is_favorite THEN 1 ELSE 0 END) as favorite_count
FROM articles
WHERE published_at IS NOT NULL
GROUP BY DATE(published_at), category;

-- Vue: weekly_trends (pour Power BI)
CREATE OR REPLACE VIEW vw_weekly_trends AS
SELECT
    DATE_TRUNC('week', date) as week_start,
    keyword,
    category,
    AVG(trend_score) as avg_trend_score,
    SUM(article_count) as total_articles
FROM trends
GROUP BY DATE_TRUNC('week', date), keyword, category;

-- Données de test pour sources
INSERT INTO sources (name, type, base_url) VALUES
    ('Reddit', 'reddit', 'https://www.reddit.com'),
    ('HackerNews', 'hackernews', 'https://news.ycombinator.com'),
    ('Dev.to', 'devto', 'https://dev.to'),
    ('GitHub Trending', 'github', 'https://github.com/trending'),
    ('Medium', 'medium', 'https://medium.com')
ON CONFLICT (name) DO NOTHING;

-- Données de test pour keywords
INSERT INTO keywords (keyword, category, weight) VALUES
    ('FHIR', 'healthtech', 4.0),
    ('blockchain', 'web3', 3.5),
    ('FastAPI', 'backend', 3.0),
    ('Next.js', 'frontend', 3.0),
    ('Python', 'dev', 2.5),
    ('TypeScript', 'dev', 2.5),
    ('AI', 'ai', 4.0),
    ('machine learning', 'ai', 3.5)
ON CONFLICT (keyword) DO NOTHING;
