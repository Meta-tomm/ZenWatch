Debug et corrige un bug en suivant cette méthodologie:

1. **Reproduction**
   - Confirme le bug
   - Identifie les steps pour reproduire
   - Note le comportement actuel vs attendu

2. **Investigation**
   - Trace le flow du code
   - Identifie la cause root
   - Vérifie les effets de bord potentiels

3. **Solution**
   - Propose 2 approches possibles
   - Explique les trade-offs
   - Recommande la meilleure

4. **Implémentation**
   - Fixe le bug de façon minimale
   - Ajoute un test de régression
   - Vérifie qu'aucun autre cas n'est cassé

5. **Validation**
   - Le bug est corrigé
   - Tests passent
   - Pas d'effet de bord

Commit avec message: `fix(scope): description courte`