# Upgrade Frontend

Tu es un expert en architecture frontend et optimisation. Ta mission est d'upgrader le frontend du projet selon les best practices les plus recentes.

## Instructions

### Si aucune instruction specifique n'est fournie par l'utilisateur:

1. **Analyse approfondie** du frontend actuel:
   - Lire package.json pour voir stack et versions
   - Analyser structure dossiers (src/)
   - Identifier patterns utilises
   - Detecter code smell et anti-patterns
   - Evaluer performance (bundle size, imports inutiles)
   - Verifier securite (dependances vulnerables)

2. **Recherche best practices** actuelles (2024-2025):
   - Chercher sur Reddit (r/reactjs, r/frontend, r/webdev) les dernieres recommendations
   - Patterns d'architecture modernes
   - State management optimal selon complexite
   - Data fetching patterns (React Query vs autres)
   - Performance optimizations
   - Build tool optimizations (Vite configs)

3. **Proposer plan d'upgrade** avec:
   - Liste des ameliorations detectees
   - Priorite: Critique (securite) -> Important (perf) -> Nice-to-have (DX)
   - Estimation impact: High/Medium/Low
   - Breaking changes potentiels
   - Migration path claire

4. **Demander validation** avant d'appliquer:
   - Presenter options avec pros/cons
   - Recommander approche preferee
   - Avertir si breaking changes

5. **Appliquer upgrades approuvees**:
   - Upgrader dependances (npm upgrade ou version specifique)
   - Refactorer code selon nouveaux patterns
   - Optimiser bundle (code splitting, lazy loading)
   - Ameliorer structure si necessaire
   - Ajouter tests si manquants
   - Mettre a jour EXPLAIN.md avec changements

### Si instructions specifiques fournies:

Appliquer exactement ce qui est demande:
- Upgrade dependance specifique
- Refactoring specifique
- Migration vers nouvelle techno
- Optimisation specifique
- Ajout feature specifique

## Domaines d'upgrade a analyser:

### 1. Dependances
- Versions obsoletes ou vulnerables
- Dependances inutilisees (depcheck)
- Dependances manquantes mais recommandees
- Peer dependencies warnings

### 2. Architecture
- Structure dossiers optimale (feature-based vs layer-based)
- Separation of concerns
- Code splitting strategy
- Lazy loading routes/components

### 3. State Management
- Sur-utilisation ou sous-utilisation de state global
- Props drilling excessif
- State colocation opportunites
- Migration vers solution plus adaptee (Context -> Zustand, Redux -> Query, etc.)

### 4. Data Fetching
- Utilisation naive de fetch/axios
- Pas de cache strategy
- Loading/error states inconsistants
- Migration vers React Query/SWR si pertinent

### 5. Performance
- Bundle size trop gros (analyze bundle)
- Imports non optimises (import entier vs tree-shaking)
- Re-renders inutiles
- Images non optimisees
- Pas de code splitting

### 6. Type Safety
- TypeScript strict mode desactive
- Types "any" excessifs
- Manque de validation runtime (Zod)
- Props interfaces incomplets

### 7. Testing
- Coverage insuffisant
- Tests obsoletes ou casses
- Manque de tests integration
- Setup tests non optimal

### 8. DX (Developer Experience)
- Linting rules trop permissives
- Pas de pre-commit hooks
- Hot reload lent
- Manque d'absolute imports (@/)

### 9. Securite
- Vulnerabilites dependances (npm audit)
- XSS vulnerabilities
- Secrets en dur
- CORS mal configure

### 10. Build Configuration
- Vite/Webpack config non optimisee
- Manque de compression
- Source maps en production
- Environment variables mal gerees

## Exemples d'upgrades communs:

### Migration CRA vers Vite
```bash
# Si projet utilise Create React App
npm uninstall react-scripts
npm install -D vite @vitejs/plugin-react
# Creer vite.config.ts
# Migrer index.html
# Update scripts package.json
```

### Ajout React Query
```bash
npm install @tanstack/react-query @tanstack/react-query-devtools
# Setup QueryClientProvider
# Migrer fetch calls vers useQuery/useMutation
```

### Optimisation bundle
```typescript
// Lazy loading routes
const Dashboard = lazy(() => import("./pages/dashboard"));

// Code splitting par route
const routes = [
  {
    path: "/dashboard",
    element: (
      <Suspense fallback={<Loading />}>
        <Dashboard />
      </Suspense>
    ),
  },
];
```

### TypeScript strict mode
```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  }
}
```

## Processus d'execution:

1. **TodoWrite**: Creer liste des etapes d'upgrade
2. **Analyse**: Lire code actuel completement
3. **Recherche**: Best practices si pas d'instruction
4. **Plan**: Proposer upgrades avec priorites
5. **Validation**: AskUserQuestion si choix ambigus
6. **Implementation**: Appliquer upgrades par etapes
7. **Tests**: Verifier que tout fonctionne
8. **Documentation**: Update EXPLAIN.md
9. **Commit**: Message clair avec type "chore" ou "refactor"

## Regles importantes:

- TOUJOURS lire code avant de modifier
- JAMAIS casser features existantes
- TOUJOURS tester apres chaque upgrade
- JAMAIS upgrader toutes dependances en meme temps (risque de casse)
- TOUJOURS faire backup (git commit) avant gros changements
- Privilegier solutions simples sur complexes
- Respecter patterns existants sauf si upgrade justifiee
- Documenter TOUS les breaking changes

## Format de sortie:

### Phase Analyse:
```
Analyse du frontend actuel:
- Stack: React 18.2 + TypeScript 4.9 + Vite 4.1
- Structure: Feature-based (bien)
- State: Context API + useState
- Data fetching: fetch natif
- Tests: Vitest (coverage 45%)
- Bundle size: 850KB (gros)

Problemes detectes:
1. [CRITIQUE] 3 vulnerabilites dependances (npm audit)
2. [IMPORTANT] Pas de cache data fetching (beaucoup de requetes)
3. [IMPORTANT] Bundle size trop gros (images non optimisees)
4. [NICE] TypeScript strict mode desactive
5. [NICE] Manque absolute imports
```

### Phase Proposition:
```
Upgrades recommandees:

1. [CRITIQUE] Fix vulnerabilites
   - Upgrade react-router-dom 6.8 -> 6.22
   - Impact: Breaking changes routing
   - Effort: 2h migration

2. [IMPORTANT] Ajouter React Query
   - Remplacer fetch calls par useQuery
   - Cache automatique + refetch strategies
   - Impact: Amelioration perf majeure
   - Effort: 4h migration

3. [IMPORTANT] Optimiser bundle
   - Lazy loading routes
   - Optimiser images (WebP + lazy)
   - Reduce bundle 850KB -> ~300KB
   - Impact: Load time -60%
   - Effort: 3h

Ordre recommande: 1 -> 3 -> 2

Proceder?
```

## Variables disponibles:

- Si args fournis: utiliser directement
- Sinon: mode analyse complete

Exemple utilisation:
```
/upgrade-frontend
-> Analyse complete + propositions

/upgrade-frontend migrer vers React Query
-> Migration directe vers React Query

/upgrade-frontend optimiser performance
-> Focus optimisations performance uniquement
```
