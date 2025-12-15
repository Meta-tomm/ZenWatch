# Commit rapide et propre

Je vais t'aider a creer un commit propre suivant les conventions.

## Etape 1: Analyse des changements

[Je vais executer git status et git diff pour voir les modifications]

## Etape 2: Categorisation

Je classe les changements par type:
- feat: Nouvelle fonctionnalite
- fix: Correction de bug
- refactor: Refactoring
- test: Ajout/modification de tests
- docs: Documentation
- style: Formatage
- chore: Maintenance
- perf: Performance

## Etape 3: Message de commit

Format: `type(scope): description`

Exemple:
- feat(auth): ajout du login JWT
- fix(invoice): correction calcul TVA
- refactor(api): simplification controllers

## Etape 4: Validation

Je verifie:
- Pas de fichiers sensibles (.env, secrets)
- Pas de console.log oublies
- Pas de code commente inutile
- Respect du .gitignore

## Etape 5: Commit

Je propose le message optimise et je commit si tu valides.

Note: Je ne mets pas trop de choses dans le message et surtout pas mon nom (Claude).
