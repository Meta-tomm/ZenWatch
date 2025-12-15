# Initialiser la structure des dossiers ZenWatch

Creer uniquement l'arborescence des dossiers du projet ZenWatch (sans fichiers de code).

## Structure a creer

```
ZenWatch/
├── .github/
│   └── workflows/
├── infra/
│   └── postgres/
├── backend-api/
│   ├── cmd/
│   │   └── server/
│   └── internal/
│       ├── config/
│       ├── database/
│       ├── handlers/
│       ├── models/
│       ├── services/
│       └── middleware/
├── ingestion-worker/
│   └── src/
└── web-client/
    └── src/
        ├── components/
        │   ├── ui/
        │   └── shared/
        ├── features/
        │   ├── dashboard/
        │   ├── settings/
        │   └── digest/
        ├── hooks/
        ├── lib/
        └── types/
```

## Execution

Creation de tous les dossiers...

PAUSE [Structure creee, verification dans l'explorateur de fichiers?]

## Resume

Arborescence ZenWatch creee avec:
- `.github/workflows/` - CI/CD
- `infra/postgres/` - Configuration infrastructure
- `backend-api/cmd/server/` + `internal/` - Backend Go
- `ingestion-worker/src/` - Worker Rust
- `web-client/src/` avec features, components, hooks - Frontend React

**Prochaines etapes:**
1. Utiliser `/init-architecture` pour generer les fichiers de code
2. Ou creer manuellement les fichiers selon tes besoins
3. Ou utiliser d'autres commandes pour ajouter des features specifiques

Architecture des dossiers prete!
