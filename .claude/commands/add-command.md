# Creer une nouvelle commande personnalisee

Je vais t'aider a creer une nouvelle commande slash personnalisee.

## Etape 1: Nom de la commande
Quel nom veux-tu donner a ta commande?
(Exemple: review-code, test-all, deploy-prod, analyze-perf)

[Attends le nom]

## Etape 2: Description rapide
En une phrase, que fait cette commande?
(Cette description apparaitra dans la liste des commandes disponibles)

[Attends la description]

## Etape 3: Type de commande

Choisis le type:
1. **Commande simple** - Execute une tache specifique avec un prompt fixe
2. **Commande interactive** - Pose des questions puis execute
3. **Commande avec mode** - Change le comportement de Claude (Mode: XXX)
4. **Workflow multi-etapes** - Plusieurs etapes sequentielles

[Attends le choix]

## Etape 4: Contenu de la commande

Base sur ton choix, voici le template:

### Pour commande simple:
```
# [Titre de la commande]

[Description de ce que Claude doit faire]

## Instructions specifiques
- [Instruction 1]
- [Instruction 2]
- [Instruction 3]

## Format de sortie
[Comment presenter les resultats]
```

### Pour commande interactive:
```
# [Titre de la commande]

## Questions
1. [Question 1]
2. [Question 2]

[Attends les reponses]

## Execution
Base sur tes reponses:
- [Action 1]
- [Action 2]
```

### Pour commande avec mode:
```
Mode: [Nom du mode]

# [Titre de la commande]

En tant que [role], je vais:
- [Comportement 1]
- [Comportement 2]

## Contraintes
- [Contrainte 1]
- [Contrainte 2]
```

### Pour workflow multi-etapes:
```
# [Titre de la commande]

## Etape 1: [Nom etape 1]
[Actions]

PAUSE [Attends validation]

## Etape 2: [Nom etape 2]
[Actions]

PAUSE [Attends validation]

## Etape 3: [Nom etape 3]
[Actions]

## Resume
[Recap de ce qui a ete fait]
```

## Etape 5: Validation

Decris-moi exactement ce que ta commande doit faire, et je vais:
1. Creer le fichier `.claude/commands/[nom].md`
2. Y ecrire le contenu optimise
3. Te montrer un exemple d'utilisation

Pret? Dis-moi ce que ta commande doit faire!
