# Correction automatique des erreurs

Je vais identifier et corriger toutes les erreurs du projet.

## Etape 1: Detection des erreurs

### TypeScript/Compilation
[Execute: tsc --noEmit ou npm run type-check]

### Linting
[Execute: npm run lint]

### Tests
[Execute: npm test]

### Build
[Execute: npm run build]

## Etape 2: Analyse et priorisation

Je classe les erreurs par:
1. **Critiques** - Bloquent le build
2. **Importantes** - Bugs potentiels
3. **Mineures** - Style, warnings

## Etape 3: Correction systematique

Pour chaque erreur:
1. Localisation (fichier:ligne)
2. Type d'erreur
3. Cause racine
4. Solution appliquee
5. Verification

## Etape 4: Validation

Apres corrections:
- Re-executer tous les checks
- Verifier que rien n'est casse
- Lancer les tests

## Etape 5: Resume

- Nombre d'erreurs corrigees
- Fichiers modifies
- Erreurs restantes (si impossibles a auto-corriger)

## Mode de correction

Par defaut: Correction automatique
Si erreur complexe: Je demande confirmation avant de modifier
