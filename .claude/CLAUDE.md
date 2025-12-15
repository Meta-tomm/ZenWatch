# ZenWatch AI - Plateforme de Veille Stratégique

## Description du projet

ZenWatch est une plateforme SaaS de veille concurrentielle "Zéro Bruit".
Le système ingère des flux de données (RSS pour le MVP) via un worker haute performance en Rust, filtre le contenu via des règles strictes, et utilise l'IA (LLM) pour générer des résumés synthétiques et des digests hebdomadaires.
L'objectif est d'offrir une expérience utilisateur (UX) fluide et visuelle, loin des agrégateurs RSS classiques.

## Stack technique

### Frontend (Dashboard)

- **Framework**: [React 18+]
- **Language**: [TypeScript]
- **Build Tool**: [Vite]
- **Styling**: [TailwindCSS] + [Shadcn/UI] (Composants)
- **State Management**: [Zustand] (Global), [TanStack Query] (Server state)
- **Icons**: [Lucide React]

### Backend (API & Orchestrator)

- **Language**: [Go 1.22+]
- **Framework**: [Chi] (Router) + [Chi-Cors]
- **Database**: [PostgreSQL 16] (Drivers: `pgx`)
- **AI Integration**: [OpenAI API / Mistral]
- **Scheduling**: [Robfig/Cron] (Pour les digests hebdo)

### Ingestion Worker (Scraper)

- **Language**: [Rust 2021]
- **Async Runtime**: [Tokio]
- **HTTP Client**: [Reqwest]
- **Parsing**: [Feed-rs] (RSS/Atom), [Scraper] (HTML)
- **Communication**: [Redis] (Pub/Sub avec le Backend)

### Infrastructure

- **Containerization**: [Docker & Docker Compose]
- **CI/CD**: [GitHub Actions]
- **Linting**: [Birome] (Frontend), [Golangci-lint] (Go), [Clippy] (Rust)

## Architecture du projet (Monorepo)

### Structure des dossiers

ZenWatch/
├── 📂 .github/ # CI/CD Workflows
├── 📂 infra/ # Docker-compose, configs Nginx/Postgres
│
├── 📂 backend-api/ # LE CERVEAU (Go)
│ ├── cmd/server/ # Entrypoint (main.go)
│ ├── internal/
│ │ ├── config/ # Variables d'env
│ │ ├── database/ # Connexion Postgres & Redis
│ │ ├── handlers/ # Contrôleurs HTTP (GET /articles)
│ │ ├── models/ # Structs DB (User, Article, Rule)
│ │ ├── services/ # Logique métier (AIService, DigestService)
│ │ └── middleware/ # Auth (JWT), Logger
│ └── go.mod
│
├── 📂 ingestion-worker/ # LE MUSCLE (Rust)
│ ├── src/
│ │ ├── main.rs # Boucle principale (Redis Consumer)
│ │ ├── fetcher.rs # Téléchargement HTTP
│ │ ├── parser.rs # Normalisation des données
│ │ └── filter.rs # Moteur de règles (Keywords)
│ └── Cargo.toml
│
└── 📂 web-client/ # LE VISAGE (React)
├── src/
│ ├── components/
│ │ ├── ui/ # Composants Shadcn (Button, Card...)
│ │ └── shared/ # Composants réutilisables
│ ├── features/ # Découpage par métier
│ │ ├── dashboard/ # Grille d'articles, Stats
│ │ ├── settings/ # Gestion des flux et keywords
│ │ └── digest/ # Vue "Newsletter hebdo"
│ ├── hooks/ # Hooks globaux (useAuth)
│ ├── lib/ # Utils (axios, date-fns)
│ └── types/ # Interfaces TypeScript
└── vite.config.ts

## Conventions de code

### Naming Conventions

- **Go**:
  - `CamelCase` pour les exports (Public).
  - `camelCase` pour le privé.
  - Acronymes en majuscules (`ServeHTTP`, `ID`, `URL`).
  - Erreurs : `err` ou `xxxErr`.
- **Rust**:
  - `snake_case` pour variables et fonctions.
  - `PascalCase` pour Structs et Enums.
  - `SCREAMING_SNAKE_CASE` pour les constantes globales.
- **TypeScript**:
  - `PascalCase` pour les composants (`ArticleCard.tsx`).
  - `camelCase` pour les variables et fonctions.
  - `usePrefix` pour les hooks.

### Structure Composant React (Exemple)

```typescript
import { useState } from 'react';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import type { Article } from '@/types';

interface ArticleCardProps {
  article: Article;
  onArchive?: (id: string) => void;
}

export const ArticleCard = ({ article, onArchive }: ArticleCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Early return si données invalides
  if (!article.title) return null;

  return (
    <div className="border rounded-lg p-4 shadow-sm hover:shadow-md transition">
      <h3 className="font-bold text-lg">{article.title}</h3>
      <div className="flex gap-2 my-2">
        {article.tags.map((tag) => (
          <Badge key={tag} variant="secondary">
            {tag}
          </Badge>
        ))}
      </div>
      {/* Contenu conditionnel */}
      {isExpanded && <p className="text-gray-600">{article.ai_summary}</p>}
    </div>
  );
};
```

## Gestion d'Erreur & Sécurité

- **Go**: TOUJOURS vérifier `if err != nil`. Wrapper les erreurs pour le contexte : `fmt.Errorf("fetching rss failed: %w", err)`.
- **Rust**: Pas de `unwrap()` en production. Utiliser `match` ou `?` (propagation). Gérer les timeouts réseau.
- **Frontend**: Utiliser des "Error Boundaries". Ne jamais afficher les stacktraces à l'utilisateur.
- **Secrets**: AUCUNE clé API (OpenAI, DB password) en dur dans le code. Utiliser `.env`.

## Instructions pour l'IA

### Comportement général

1.  **Context Awareness**: Avant de proposer du code, vérifie dans quel dossier tu te trouves (`backend-api`, `ingestion-worker` ou `web-client`).
2.  **Type Safety**:
    - **TypeScript** : Pas de `any`.
    - **Go** : Utiliser des structs typés pour les requêtes JSON.
    - **Rust** : Utiliser le système de types fort.
3.  **Performance First**:
    - Le worker Rust doit être non-bloquant.
    - Le Frontend doit utiliser la pagination ou l'infinite scroll.

### Ce que tu dois faire

- Proposer des solutions modulaires (ex: un service dédié pour l'IA côté Go).
- Écrire les tests unitaires pour la logique critique (ex: le filtrage des mots-clés en Rust).
- Utiliser les composants **Shadcn/UI** existants plutôt que de recréer du CSS.

### Ce que tu ne dois PAS faire

- Modifier la configuration Docker sans demande explicite.
- Introduire des librairies lourdes si une solution native existe (ex: utiliser `fetch` ou `axios` léger, pas de jQuery).
- Laisser des `console.log` ou `fmt.Println` de debug.

## Commandes Utiles

### Infrastructure

```bash
docker-compose up -d       # Lancer DB + Redis
```
