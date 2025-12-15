# Setup Git et liaison repo GitHub

Initialiser un repo Git local et le lier a un repo GitHub distant (SSH ou HTTPS).

## Etape 1: Verification

Verifie si Git est installe et affiche la version.

PAUSE [Git installe?]

## Etape 2: Questions

1. **URL du repo GitHub** (SSH ou HTTPS) :
   - Format SSH : `git@github.com:username/repo.git`
   - Format HTTPS : `https://github.com/username/repo.git`

[Attends l'URL]

2. **Nom de la branche principale** :
   - Par defaut : `main`
   - Autre : `master`, `develop`, etc.

[Attends le nom de branche ou utilise "main" par defaut]

## Etape 3: Verification repo existant

Verifie si un repo Git existe deja dans le dossier courant.

Si oui :
- Afficher les remotes existantes
- Proposer de :
  1. Remplacer l'origine existante
  2. Ajouter une nouvelle remote avec un autre nom
  3. Annuler

Si non :
- Continuer l'initialisation

PAUSE [Validation action?]

## Etape 4: Initialisation Git

Execute les commandes :

```bash
# Si pas de repo existant
git init

# Renommer la branche
git branch -M [nom-branche]

# Ajouter le remote
git remote add origin [url-repo]

# Verifier
git remote -v
```

PAUSE [Commandes executees, verification?]

## Etape 5: Premier commit (optionnel)

Proposer de faire un premier commit si des fichiers existent :

```bash
# Voir les fichiers
git status

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "chore: initial commit"
```

Veux-tu faire le premier commit maintenant ?

[Attends reponse: oui/non]

Si oui, execute les commandes.

PAUSE [Commit effectue?]

## Etape 6: Push initial (optionnel)

Proposer de push sur GitHub :

```bash
git push -u origin [nom-branche]
```

Attention : Le repo distant doit exister sur GitHub avant de push.

Veux-tu push maintenant ?

[Attends reponse: oui/non]

Si oui, execute la commande.

PAUSE [Push effectue?]

## Resume

Configuration Git completee :

- Repo Git initialise : ✓
- Branche principale : `[nom-branche]`
- Remote origin : `[url-repo]`
- Type de connexion : [SSH/HTTPS detecte automatiquement]
- Premier commit : [oui/non]
- Push initial : [oui/non]

## Prochaines etapes

1. **Si SSH** : Verifie que ta cle SSH est bien configuree sur GitHub
   ```bash
   ssh -T git@github.com
   ```

2. **Si HTTPS** : Tu devras t'authentifier lors du premier push
   - Utilise un Personal Access Token (pas le mot de passe)
   - Configure les credentials :
     ```bash
     git config credential.helper store
     ```

3. **Configurer ton identite Git** (si pas deja fait) :
   ```bash
   git config user.name "Ton Nom"
   git config user.email "ton@email.com"
   ```

4. **Workflow standard** :
   ```bash
   git add .
   git commit -m "type(scope): message"
   git push
   ```

Repo Git pret pour le developpement !
