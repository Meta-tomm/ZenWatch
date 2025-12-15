# Initialiser l'architecture ZenWatch

Creer l'architecture complete du projet ZenWatch (backend Go, worker Rust, frontend React).

## Etape 1: Verification prerequis

Verifie la presence de:

- Go 1.22+
- Rust 2021+
- Node.js 18+
- Docker & Docker Compose

Affiche les versions installees.

PAUSE [Validation: tout est installe?]

## Etape 2: Structure des dossiers

Creer l'arborescence complete:

```
ZenWatch/
├── .github/
│   └── workflows/
│       ├── backend.yml
│       ├── worker.yml
│       └── frontend.yml
├── infra/
│   ├── docker-compose.yml
│   └── postgres/
│       └── init.sql
├── backend-api/
│   ├── cmd/
│   │   └── server/
│   │       └── main.go
│   ├── internal/
│   │   ├── config/
│   │   ├── database/
│   │   ├── handlers/
│   │   ├── models/
│   │   ├── services/
│   │   └── middleware/
│   ├── go.mod
│   └── go.sum
├── ingestion-worker/
│   ├── src/
│   │   ├── main.rs
│   │   ├── fetcher.rs
│   │   ├── parser.rs
│   │   └── filter.rs
│   ├── Cargo.toml
│   └── Cargo.lock
├── web-client/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   └── shared/
│   │   ├── features/
│   │   │   ├── dashboard/
│   │   │   ├── settings/
│   │   │   └── digest/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── tailwind.config.js
├── .gitignore
├── .env.example
└── README.md
```

PAUSE [Structure creee, verification visuelle?]

## Etape 3: Backend Go - Fichiers de base

### 3.1 go.mod

```go
module zenwatch/backend-api

go 1.22

require (
    github.com/go-chi/chi/v5 v5.0.11
    github.com/go-chi/cors v1.2.1
    github.com/jackc/pgx/v5 v5.5.1
    github.com/robfig/cron/v3 v3.0.1
    github.com/redis/go-redis/v9 v9.4.0
    github.com/joho/godotenv v1.5.1
)
```

### 3.2 cmd/server/main.go

```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
    "github.com/go-chi/cors"
    "github.com/joho/godotenv"
)

func main() {
    // Load environment variables
    if err := godotenv.Load(); err != nil {
        log.Println("No .env file found")
    }

    // Create router
    r := chi.NewRouter()

    // Middleware
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(cors.Handler(cors.Options{
        AllowedOrigins:   []string{"http://localhost:5173"},
        AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
        AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type"},
        AllowCredentials: true,
    }))

    // Health check
    r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("OK"))
    })

    // API routes
    r.Route("/api/v1", func(r chi.Router) {
        r.Get("/articles", func(w http.ResponseWriter, r *http.Request) {
            w.Write([]byte("Articles endpoint"))
        })
    })

    // Server setup
    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    srv := &http.Server{
        Addr:         ":" + port,
        Handler:      r,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    // Graceful shutdown
    go func() {
        log.Printf("Server starting on port %s", port)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("Server failed: %v", err)
        }
    }()

    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    log.Println("Shutting down server...")
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        log.Fatalf("Server forced to shutdown: %v", err)
    }

    log.Println("Server exited")
}
```

### 3.3 internal/config/config.go

```go
package config

import (
    "os"
)

type Config struct {
    Port        string
    DatabaseURL string
    RedisURL    string
    OpenAIKey   string
}

func Load() *Config {
    return &Config{
        Port:        getEnv("PORT", "8080"),
        DatabaseURL: getEnv("DATABASE_URL", "postgres://zenwatch:password@localhost:5432/zenwatch?sslmode=disable"),
        RedisURL:    getEnv("REDIS_URL", "localhost:6379"),
        OpenAIKey:   getEnv("OPENAI_API_KEY", ""),
    }
}

func getEnv(key, fallback string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return fallback
}
```

PAUSE [Backend Go cree, verification?]

## Etape 4: Worker Rust - Fichiers de base

### 4.1 Cargo.toml

```toml
[package]
name = "ingestion-worker"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1.35", features = ["full"] }
reqwest = { version = "0.11", features = ["json"] }
feed-rs = "1.4"
scraper = "0.18"
redis = { version = "0.24", features = ["tokio-comp", "connection-manager"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
thiserror = "1.0"
tracing = "0.1"
tracing-subscriber = "0.3"
dotenv = "0.15"
```

### 4.2 src/main.rs

```rust
use dotenv::dotenv;
use std::env;
use tracing::{info, error};

mod fetcher;
mod parser;
mod filter;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load environment variables
    dotenv().ok();

    // Initialize tracing
    tracing_subscriber::fmt::init();

    info!("Starting ZenWatch Ingestion Worker");

    // Redis connection
    let redis_url = env::var("REDIS_URL").unwrap_or_else(|_| "redis://127.0.0.1:6379".to_string());
    let client = redis::Client::open(redis_url)?;
    let mut con = client.get_async_connection().await?;

    info!("Connected to Redis");

    // Main worker loop
    loop {
        match process_feeds(&mut con).await {
            Ok(_) => info!("Feed processing cycle completed"),
            Err(e) => error!("Feed processing error: {}", e),
        }

        // Wait before next cycle
        tokio::time::sleep(tokio::time::Duration::from_secs(300)).await;
    }
}

async fn process_feeds(con: &mut redis::aio::Connection) -> Result<(), Box<dyn std::error::Error>> {
    // Placeholder for feed processing logic
    Ok(())
}
```

### 4.3 src/fetcher.rs

```rust
use reqwest;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum FetchError {
    #[error("HTTP request failed: {0}")]
    RequestFailed(#[from] reqwest::Error),
    #[error("Invalid URL: {0}")]
    InvalidUrl(String),
}

pub async fn fetch_feed(url: &str) -> Result<String, FetchError> {
    let response = reqwest::get(url).await?;
    let body = response.text().await?;
    Ok(body)
}
```

### 4.4 src/parser.rs

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Article {
    pub title: String,
    pub url: String,
    pub content: String,
    pub published_at: Option<String>,
}

pub fn parse_rss(content: &str) -> Result<Vec<Article>, Box<dyn std::error::Error>> {
    // Placeholder for RSS parsing
    Ok(Vec::new())
}
```

### 4.5 src/filter.rs

```rust
use crate::parser::Article;

pub struct FilterRule {
    pub keywords: Vec<String>,
    pub exclude_keywords: Vec<String>,
}

pub fn apply_filters(articles: Vec<Article>, rules: &FilterRule) -> Vec<Article> {
    articles
        .into_iter()
        .filter(|article| matches_filters(article, rules))
        .collect()
}

fn matches_filters(article: &Article, rules: &FilterRule) -> bool {
    let content_lower = article.content.to_lowercase();
    let title_lower = article.title.to_lowercase();

    // Check if any keyword matches
    let has_keyword = rules.keywords.iter().any(|kw| {
        content_lower.contains(&kw.to_lowercase()) || title_lower.contains(&kw.to_lowercase())
    });

    // Check if any exclude keyword matches
    let has_exclude = rules.exclude_keywords.iter().any(|kw| {
        content_lower.contains(&kw.to_lowercase()) || title_lower.contains(&kw.to_lowercase())
    });

    has_keyword && !has_exclude
}
```

PAUSE [Worker Rust cree, verification?]

## Etape 5: Frontend React - Fichiers de base

### 5.1 package.json

```json
{
  "name": "zenwatch-web-client",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "date-fns": "^3.0.6",
    "lucide-react": "^0.303.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.47",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.10",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

### 5.2 vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
});
```

### 5.3 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 5.4 src/main.tsx

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
```

### 5.5 src/App.tsx

```typescript
import { useState } from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">ZenWatch</h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600">Plateforme de veille stratégique "Zéro Bruit"</p>
        </div>
      </main>
    </div>
  );
}

export default App;
```

### 5.6 src/index.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 5.7 tailwind.config.js

```javascript
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

PAUSE [Frontend React cree, verification?]

## Etape 6: Infrastructure

### 6.1 infra/docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: zenwatch-postgres
    environment:
      POSTGRES_USER: zenwatch
      POSTGRES_PASSWORD: password
      POSTGRES_DB: zenwatch
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    container_name: zenwatch-redis
    ports:
      - '6379:6379'
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 6.2 infra/postgres/init.sql

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Articles table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000) UNIQUE NOT NULL,
    content TEXT,
    ai_summary TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rules table
CREATE TABLE rules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    keywords TEXT[],
    exclude_keywords TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_articles_published ON articles(published_at);
CREATE INDEX idx_articles_created ON articles(created_at);
```

### 6.3 .env.example

```env
# Backend
PORT=8080
DATABASE_URL=postgres://zenwatch:password@localhost:5432/zenwatch?sslmode=disable
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-your-key-here

# Worker
RUST_LOG=info

# Frontend (Vite)
VITE_API_URL=http://localhost:8080/api/v1
```

### 6.4 .gitignore

```
# Dependencies
node_modules/
target/

# Build outputs
dist/
build/
*.exe

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite
```

PAUSE [Infrastructure creee, verification?]

## Etape 7: CI/CD GitHub Actions

### 7.1 .github/workflows/backend.yml

```yaml
name: Backend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend-api/**'
  pull_request:
    paths:
      - 'backend-api/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - name: Run tests
        working-directory: backend-api
        run: |
          go test ./...
      - name: Lint
        working-directory: backend-api
        run: |
          go vet ./...
```

### 7.2 .github/workflows/worker.yml

```yaml
name: Worker CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'ingestion-worker/**'
  pull_request:
    paths:
      - 'ingestion-worker/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - name: Run tests
        working-directory: ingestion-worker
        run: cargo test
      - name: Clippy
        working-directory: ingestion-worker
        run: cargo clippy -- -D warnings
```

### 7.3 .github/workflows/frontend.yml

```yaml
name: Frontend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'web-client/**'
  pull_request:
    paths:
      - 'web-client/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install dependencies
        working-directory: web-client
        run: npm ci
      - name: Type check
        working-directory: web-client
        run: npm run build
      - name: Lint
        working-directory: web-client
        run: npm run lint
```

PAUSE [CI/CD cree, verification?]

## Etape 8: README.md

````markdown
# ZenWatch - Plateforme de Veille Stratégique "Zéro Bruit"

Plateforme SaaS de veille concurrentielle avec ingestion RSS, filtrage intelligent et résumés IA.

## Stack Technique

- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Backend**: Go 1.22+ + Chi + PostgreSQL 16
- **Worker**: Rust 2021 + Tokio + Redis
- **Infrastructure**: Docker Compose

## Démarrage rapide

### 1. Prérequis

- Go 1.22+
- Rust 2021+
- Node.js 18+
- Docker & Docker Compose

### 2. Infrastructure

```bash
cd infra
docker-compose up -d
```
````

### 3. Backend

```bash
cd backend-api
cp ../.env.example .env
go mod download
go run cmd/server/main.go
```

### 4. Worker

```bash
cd ingestion-worker
cp ../.env.example .env
cargo run
```

### 5. Frontend

```bash
cd web-client
npm install
npm run dev
```

## URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8080
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Architecture

```
ZenWatch/
├── backend-api/      # API Go (port 8080)
├── ingestion-worker/ # Worker Rust
├── web-client/       # React frontend (port 5173)
└── infra/            # Docker Compose
```

## Commandes utiles

```bash
# Tests
cd backend-api && go test ./...
cd ingestion-worker && cargo test
cd web-client && npm test

# Linting
cd backend-api && go vet ./...
cd ingestion-worker && cargo clippy
cd web-client && npm run lint

# Build
cd backend-api && go build -o bin/server cmd/server/main.go
cd ingestion-worker && cargo build --release
cd web-client && npm run build
```

## Documentation

Voir `.claude/CLAUDE.md` pour les conventions et l'architecture détaillée.

````

PAUSE [README cree, verification?]

## Etape 9: Premier commit

Execute:
```bash
git init
git add .
git commit -m "chore: initial project setup

- Backend Go avec Chi router et structure modulaire
- Worker Rust avec Tokio et Redis
- Frontend React avec TypeScript et Vite
- Docker Compose pour PostgreSQL et Redis
- CI/CD GitHub Actions
- Configuration linting et formatting"
````

PAUSE [Commit effectue?]

## Resume

Architecture ZenWatch creee avec:

**Backend Go** (`backend-api/`)

- Server Chi avec CORS et middleware
- Structure modulaire (config, handlers, models, services)
- Health check et routes API de base
- Configuration PostgreSQL et Redis

**Worker Rust** (`ingestion-worker/`)

- Runtime Tokio asynchrone
- Modules fetcher, parser, filter
- Connexion Redis pour pub/sub
- Gestion erreurs avec thiserror

**Frontend React** (`web-client/`)

- React 18 + TypeScript strict
- Vite avec alias @/ et proxy API
- TailwindCSS pour styling
- TanStack Query pour state serveur

**Infrastructure** (`infra/`)

- Docker Compose (PostgreSQL 16 + Redis 7)
- Schema SQL initial
- Variables environnement

**CI/CD**

- GitHub Actions pour chaque composant
- Tests + Linting automatiques

**Prochaines etapes:**

1. Lancer infrastructure: `cd infra && docker-compose up -d`
2. Tester backend: `cd backend-api && go run cmd/server/main.go`
3. Tester worker: `cd ingestion-worker && cargo run`
4. Tester frontend: `cd web-client && npm install && npm run dev`
5. Implementer la logique metier selon besoins

Architecture prete pour le developpement!
