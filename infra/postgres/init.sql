-- ZenWatch Database Schema
-- MVP: Users, Articles, Rules (sans IA pour l'instant)

-- Table des utilisateurs
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des articles RSS
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000) UNIQUE NOT NULL,
    content TEXT,
    published_at TIMESTAMP,
    ai_summary TEXT,  -- NULL pour l'instant, pour l'IA plus tard
    source VARCHAR(255),  -- Nom du flux RSS
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des règles de filtrage
CREATE TABLE rules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    keywords TEXT[] NOT NULL DEFAULT '{}',  -- Mots-clés à inclure
    exclude_keywords TEXT[] NOT NULL DEFAULT '{}',  -- Mots-clés à exclure
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les performances
CREATE INDEX idx_articles_published ON articles(published_at DESC);
CREATE INDEX idx_articles_created ON articles(created_at DESC);
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_rules_user ON rules(user_id);

-- Commentaires pour la documentation
COMMENT ON TABLE users IS 'Utilisateurs de la plateforme ZenWatch';
COMMENT ON TABLE articles IS 'Articles récupérés des flux RSS';
COMMENT ON TABLE rules IS 'Règles de filtrage par utilisateur';
COMMENT ON COLUMN articles.ai_summary IS 'Résumé généré par IA (ajouté plus tard)';
