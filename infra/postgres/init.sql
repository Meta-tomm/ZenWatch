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

-- Table: scraping_runs
CREATE TABLE IF NOT EXISTS scraping_runs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE,
    source_type VARCHAR(50) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    articles_scraped INTEGER DEFAULT 0,
    articles_saved INTEGER DEFAULT 0,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_scraping_runs_task_id ON scraping_runs(task_id);

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

-- Données de base pour sources
INSERT INTO sources (name, type, base_url) VALUES
    ('Reddit', 'reddit', 'https://www.reddit.com'),
    ('HackerNews', 'hackernews', 'https://news.ycombinator.com'),
    ('Dev.to', 'devto', 'https://dev.to'),
    ('GitHub Trending', 'github', 'https://github.com/trending'),
    ('Medium', 'medium', 'https://medium.com'),
    ('YouTube Trending', 'youtube_trending', 'https://www.youtube.com/feed/trending'),
    ('YouTube Tech RSS', 'youtube_rss', 'https://www.youtube.com/feeds/videos.xml')
ON CONFLICT (name) DO NOTHING;

-- Keywords par défaut - Claude & AI Focus
INSERT INTO keywords (keyword, category, weight) VALUES
    -- Claude (priorité maximale)
    ('Claude', 'ai', 5.0),
    ('Claude Code', 'ai', 5.0),
    ('Claude Sonnet', 'ai', 5.0),
    ('Claude Opus', 'ai', 5.0),
    ('Claude Haiku', 'ai', 5.0),
    ('Claude 3', 'ai', 5.0),
    ('Claude 4', 'ai', 5.0),
    ('Claude MCP', 'ai', 5.0),
    ('Anthropic', 'ai', 5.0),
    ('Claude API', 'ai', 4.0),
    ('Claude Desktop', 'ai', 4.0),
    ('Claude Pro', 'ai', 4.0),
    ('Claude artifacts', 'ai', 4.0),
    -- AI General (haute priorité)
    ('agentic AI', 'ai', 5.0),
    ('autonomous agents', 'ai', 5.0),
    ('AI', 'ai', 4.0),
    ('LLM', 'ai', 4.0),
    ('MCP', 'ai', 4.0),
    ('RAG', 'ai', 4.0),
    ('GPT', 'ai', 3.0),
    ('fine-tuning', 'ai', 3.0),
    ('transformer', 'ai', 3.0),
    ('machine learning', 'ai', 3.0),
    -- Dev tools
    ('FastAPI', 'backend', 3.0),
    ('Next.js', 'frontend', 3.0),
    ('Python', 'dev', 2.5),
    ('TypeScript', 'dev', 2.5)
ON CONFLICT (keyword) DO NOTHING;

-- Table: youtube_channels (pour RSS scraping)
CREATE TABLE IF NOT EXISTS youtube_channels (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(255) NOT NULL UNIQUE,
    channel_name VARCHAR(255) NOT NULL,
    channel_url TEXT NOT NULL,
    rss_feed_url TEXT NOT NULL,
    thumbnail_url TEXT,
    subscriber_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_suggested BOOLEAN DEFAULT FALSE,
    suggestion_score FLOAT,
    suggestion_reason TEXT,
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_youtube_channels_active ON youtube_channels(is_active);

CREATE TRIGGER update_youtube_channels_updated_at BEFORE UPDATE ON youtube_channels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- YouTube Channels par défaut - AI & Dev
INSERT INTO youtube_channels (channel_id, channel_name, channel_url, rss_feed_url, is_active) VALUES
-- AI Focused
('UCWN3xxRkmTPmbKwht9FuE5A', 'Siraj Raval', 'https://www.youtube.com/@SirajRaval', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCWN3xxRkmTPmbKwht9FuE5A', true),
('UCZHmQk67mSJgfCCTn7xBfew', 'Yannic Kilcher', 'https://www.youtube.com/@YannicKilcher', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCZHmQk67mSJgfCCTn7xBfew', true),
('UCbfYPyITQ-7l4upoX8nvctg', 'Two Minute Papers', 'https://www.youtube.com/@TwoMinutePapers', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCbfYPyITQ-7l4upoX8nvctg', true),
('UCUzGQrN-lyyc0BWTYoJM_Sg', 'AI Explained', 'https://www.youtube.com/@aiaboratory', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCUzGQrN-lyyc0BWTYoJM_Sg', true),
('UCMLtBahI5DMrt0NPvDSoIRQ', 'Machine Learning Street Talk', 'https://www.youtube.com/@MachineLearningStreetTalk', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCMLtBahI5DMrt0NPvDSoIRQ', true),
('UC0RhatS1pyxInC00YKjjBqQ', 'Andrej Karpathy', 'https://www.youtube.com/@AndrejKarpathy', 'https://www.youtube.com/feeds/videos.xml?channel_id=UC0RhatS1pyxInC00YKjjBqQ', true),
('UCr8O8l5cCX85Oem1d18EezQ', 'The AI Epiphany', 'https://www.youtube.com/@TheAIEpiphany', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCr8O8l5cCX85Oem1d18EezQ', true),
('UCgBncpylJ1kiVaPyP-PZauQ', 'Lex Fridman', 'https://www.youtube.com/@lexfridman', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCgBncpylJ1kiVaPyP-PZauQ', true),
('UC9-y-6csu5WGm29I7JiwpnA', 'Computerphile', 'https://www.youtube.com/@Computerphile', 'https://www.youtube.com/feeds/videos.xml?channel_id=UC9-y-6csu5WGm29I7JiwpnA', true),
('UCvjgXvBlbQiY_fTHQYCwXJQ', 'Arxiv Insights', 'https://www.youtube.com/@ArxivInsights', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCvjgXvBlbQiY_fTHQYCwXJQ', true),
('UCpVm7bg6pXKo1Pr6k5kxG9A', 'Matthew Berman', 'https://www.youtube.com/@matthew_berman', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCpVm7bg6pXKo1Pr6k5kxG9A', true),
('UCJIfeSCssxSC_Dhc5s7woww', 'Sam Witteveen', 'https://www.youtube.com/@samwitteveen', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCJIfeSCssxSC_Dhc5s7woww', true),
('UC6vRUjN6o2CWWQRY_AVQMag', 'AI Jason', 'https://www.youtube.com/@AIJasonZ', 'https://www.youtube.com/feeds/videos.xml?channel_id=UC6vRUjN6o2CWWQRY_AVQMag', true),
('UCLLw7jmFsvfIVaUFsLs8mlQ', 'Luke Barousse', 'https://www.youtube.com/@LukeBarousse', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCLLw7jmFsvfIVaUFsLs8mlQ', true),
('UCZsyNx73TNLlIxLU7q8cOGg', 'Nicholas Renotte', 'https://www.youtube.com/@NicholasRenotte', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCZsyNx73TNLlIxLU7q8cOGg', true),
-- Dev & Programming
('UCsBjURrPoezykLs9EqgamOA', 'Fireship', 'https://www.youtube.com/@Fireship', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCsBjURrPoezykLs9EqgamOA', true),
('UCW5YeuERMmlnqo4oq8vwUpg', 'The Net Ninja', 'https://www.youtube.com/@NetNinja', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCW5YeuERMmlnqo4oq8vwUpg', true),
('UC8butISFwT-Wl7EV0hUK0BQ', 'freeCodeCamp', 'https://www.youtube.com/@freecodecamp', 'https://www.youtube.com/feeds/videos.xml?channel_id=UC8butISFwT-Wl7EV0hUK0BQ', true),
('UCFbNIlppjAuEX4znoulh0Cw', 'Web Dev Simplified', 'https://www.youtube.com/@WebDevSimplified', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCFbNIlppjAuEX4znoulh0Cw', true),
('UC29ju8bIPH5as8OGnQzwJyA', 'Traversy Media', 'https://www.youtube.com/@TraversyMedia', 'https://www.youtube.com/feeds/videos.xml?channel_id=UC29ju8bIPH5as8OGnQzwJyA', true),
('UCnUYZLuoy1rq1aVMwx4aTzw', 'CS Dojo', 'https://www.youtube.com/@CSDojo', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCnUYZLuoy1rq1aVMwx4aTzw', true),
('UCWX3yGzq9Fnu8Y6g-RRz5LA', 'Theo - t3.gg', 'https://www.youtube.com/@t3dotgg', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCWX3yGzq9Fnu8Y6g-RRz5LA', true),
('UCmXmlB4-HJytD7wek0Uo97A', 'JavaScript Mastery', 'https://www.youtube.com/@javascriptmastery', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCmXmlB4-HJytD7wek0Uo97A', true),
('UC-8QAzbLcRglXeN_MY9blyw', 'Ben Holmes', 'https://www.youtube.com/@bholmesdev', 'https://www.youtube.com/feeds/videos.xml?channel_id=UC-8QAzbLcRglXeN_MY9blyw', true),
-- Famous Tech
('UCBcRF18a7Qf58cCRy5xuWwQ', 'MKBHD', 'https://www.youtube.com/@mkbhd', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ', true),
('UCddiUEpeqJcYeBxX1IVBKvQ', 'The Verge', 'https://www.youtube.com/@TheVerge', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCddiUEpeqJcYeBxX1IVBKvQ', true),
('UCVYamHliCI9rw1tHR1xbkfw', 'Dave2D', 'https://www.youtube.com/@Dave2D', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCVYamHliCI9rw1tHR1xbkfw', true)
ON CONFLICT (channel_id) DO NOTHING;
