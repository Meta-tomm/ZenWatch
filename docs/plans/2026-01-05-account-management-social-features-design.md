# Design: Account Management & Social Features

**Date**: 2026-01-05
**Status**: Validated
**Auteur**: Tom (Epitech Lyon)

---

## 1. Vue d'ensemble

**Objectif**: Transformer ZenWatch d'un systeme single-user en plateforme communautaire multi-utilisateurs pour devs/passionnes d'IA.

### Composants principaux

1. **Systeme d'authentification**
   - OAuth: GitHub, Google, Discord
   - Fallback email/password avec verification email
   - Sessions JWT (access token + refresh token)

2. **Modele utilisateur**
   - Profil dev-oriented (pseudo, avatar, bio, liens)
   - 2 roles: User / Admin
   - Donnees personnelles isolees (favoris, historique lecture)

3. **Systeme de mots-cles hybride**
   - Keywords globaux (base, geres par admin) - ciblent le contenu IA/dev
   - Keywords personnels (ajoutes par chaque user pour affiner)
   - Le scoring combine les deux

4. **Commentaires threaded**
   - Style Reddit: commentaires + reponses imbriquees
   - Attaches aux articles ET videos
   - Moderation par admins

5. **Panel admin**
   - CRUD complet: Users, Contenu, Keywords globaux, Commentaires
   - Dashboard stats et moderation

### Donnees globales vs personnelles

| Type | Donnees |
|------|---------|
| Global | articles, videos, sources, keywords de base, likes/dislikes (score public) |
| Personnel | favoris, statut "lu", keywords perso, preferences |

---

## 2. Schema Base de Donnees

### 2.1 Nouvelles Tables

#### `users`
Remplace le concept email-only de `user_config`.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- NULL si OAuth only
    avatar_url TEXT,
    bio VARCHAR(500),
    github_url TEXT,
    portfolio_url TEXT,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `oauth_accounts`
Lie users aux providers OAuth.

```sql
CREATE TABLE oauth_accounts (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('github', 'google', 'discord')),
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    access_token TEXT,  -- encrypted
    refresh_token TEXT,  -- encrypted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id)
);
```

#### `user_article_states`
Favoris et statut lu par utilisateur.

```sql
CREATE TABLE user_article_states (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    is_read BOOLEAN DEFAULT false,
    is_favorite BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, article_id)
);
```

#### `user_video_states`
Meme logique pour videos.

```sql
CREATE TABLE user_video_states (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    is_read BOOLEAN DEFAULT false,
    is_favorite BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, video_id)
);
```

#### `user_keywords`
Keywords personnels en plus des globaux.

```sql
CREATE TABLE user_keywords (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    keyword VARCHAR(100) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, keyword)
);
```

#### `comments`
Commentaires threaded (style Reddit).

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (article_id IS NOT NULL OR video_id IS NOT NULL)
);

CREATE INDEX idx_comments_article ON comments(article_id) WHERE article_id IS NOT NULL;
CREATE INDEX idx_comments_video ON comments(video_id) WHERE video_id IS NOT NULL;
CREATE INDEX idx_comments_parent ON comments(parent_id) WHERE parent_id IS NOT NULL;
```

#### `user_consents` (RGPD)
Tracking des consentements utilisateur.

```sql
CREATE TABLE user_consents (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    consent_type VARCHAR(50) NOT NULL CHECK (consent_type IN ('terms', 'privacy', 'marketing', 'analytics')),
    consented BOOLEAN NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    consented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    withdrawn_at TIMESTAMP
);
```

#### `data_export_requests` (RGPD)
Droit d'acces aux donnees.

```sql
CREATE TABLE data_export_requests (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'expired')),
    file_url TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

### 2.2 Tables Modifiees

#### `user_config`
Ajoute liaison vers `users`.

```sql
ALTER TABLE user_config
ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE;

-- Migration: creer users depuis emails existants, puis lier
```

#### `keywords`
Devient admin-only pour les globaux (pas de changement schema, juste permissions API).

---

## 3. Structure API Backend

### 3.1 Nouveaux Routers

#### `auth.py` - `/api/auth`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Inscription email/password |
| POST | `/auth/login` | Connexion email/password |
| POST | `/auth/logout` | Deconnexion (invalide refresh token) |
| POST | `/auth/refresh` | Renouvelle access token |
| POST | `/auth/forgot-password` | Demande reset password |
| POST | `/auth/reset-password` | Reset avec token |
| GET | `/auth/verify-email/{token}` | Verification email |
| GET | `/auth/oauth/{provider}` | Redirect vers OAuth |
| GET | `/auth/oauth/{provider}/callback` | Callback OAuth |

#### `users.py` - `/api/users`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Profil utilisateur connecte |
| PATCH | `/users/me` | Update profil |
| PATCH | `/users/me/avatar` | Upload avatar |
| DELETE | `/users/me` | Suppression compte (RGPD) |
| GET | `/users/me/export` | Demande export donnees (RGPD) |
| GET | `/users/{id}/profile` | Profil public d'un user |

#### `user-keywords.py` - `/api/user-keywords`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user-keywords` | Liste keywords perso |
| POST | `/user-keywords` | Ajoute keyword perso |
| DELETE | `/user-keywords/{id}` | Supprime keyword perso |

#### `comments.py` - `/api/comments`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/comments/article/{id}` | Commentaires d'un article (threaded) |
| GET | `/comments/video/{id}` | Commentaires d'une video |
| POST | `/comments` | Cree commentaire |
| PATCH | `/comments/{id}` | Edite son commentaire |
| DELETE | `/comments/{id}` | Supprime son commentaire (soft delete) |

#### `admin.py` - `/api/admin`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | Liste tous les users |
| PATCH | `/admin/users/{id}` | Modifier user (role, is_active) |
| DELETE | `/admin/users/{id}` | Supprimer user |
| DELETE | `/admin/articles/{id}` | Supprimer article |
| DELETE | `/admin/videos/{id}` | Supprimer video |
| GET | `/admin/comments` | Liste commentaires (moderation) |
| DELETE | `/admin/comments/{id}` | Hard delete commentaire |
| PATCH | `/admin/comments/{id}/restore` | Restore commentaire |

### 3.2 Routes Modifiees

```python
# articles.py - ajoute middleware auth optionnel
GET /articles         # Retourne aussi is_read/is_favorite du user connecte
PATCH /articles/{id}/read     # Maintenant lie au user connecte
PATCH /articles/{id}/favorite # Maintenant lie au user connecte

# keywords.py - devient admin-only pour les globaux
POST/PATCH/DELETE /keywords   # Requiert role admin
GET /keywords                 # Reste public (keywords de base)
```

### 3.3 Middleware Auth

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Requiert authentification."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    """Auth optionnelle - retourne None si pas connecte."""
    if not token:
        return None
    return await verify_token(token)

async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Requiert role admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return user
```

---

## 4. Structure Frontend

### 4.1 Nouvelles Pages

```
app/
├── (auth)/                      # Layout sans sidebar
│   ├── login/page.tsx
│   ├── register/page.tsx
│   ├── forgot-password/page.tsx
│   └── reset-password/page.tsx
│
├── profile/
│   ├── page.tsx                 # Mon profil (edition)
│   └── [username]/page.tsx      # Profil public
│
├── admin/                       # Layout admin
│   ├── layout.tsx
│   ├── page.tsx                 # Dashboard
│   ├── users/page.tsx
│   ├── content/page.tsx
│   ├── keywords/page.tsx
│   └── comments/page.tsx
│
├── settings/
│   └── page.tsx                 # Preferences + RGPD
```

### 4.2 Nouveaux Composants

```
components/
├── auth/
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   ├── OAuthButtons.tsx
│   └── AuthGuard.tsx
│
├── comments/
│   ├── CommentSection.tsx
│   ├── CommentThread.tsx
│   ├── CommentForm.tsx
│   └── CommentCard.tsx
│
├── profile/
│   ├── ProfileCard.tsx
│   ├── ProfileEditForm.tsx
│   └── AvatarUpload.tsx
│
├── admin/
│   ├── AdminSidebar.tsx
│   ├── UserTable.tsx
│   ├── ContentTable.tsx
│   ├── CommentModerationTable.tsx
│   └── StatsCards.tsx
│
├── settings/
│   ├── UserKeywordManager.tsx
│   ├── PrivacySettings.tsx
│   └── ConsentManager.tsx
```

### 4.3 Nouveaux Hooks

```typescript
// hooks/useAuth.ts
export function useAuth() {
  const login = async (email: string, password: string) => { ... }
  const register = async (data: RegisterData) => { ... }
  const logout = async () => { ... }
  const loginWithOAuth = (provider: 'github' | 'google' | 'discord') => { ... }
  return { login, register, logout, loginWithOAuth }
}

// hooks/useCurrentUser.ts
export function useCurrentUser() {
  return useAuthStore((state) => state.user)
}

// hooks/useComments.ts
export function useComments(type: 'article' | 'video', id: string) { ... }
export function useCreateComment() { ... }
export function useDeleteComment() { ... }

// hooks/useUserKeywords.ts
export function useUserKeywords() { ... }
export function useCreateUserKeyword() { ... }
export function useDeleteUserKeyword() { ... }

// hooks/useAdmin.ts
export function useAdminUsers() { ... }
export function useAdminComments() { ... }
```

### 4.4 Auth Store (Zustand)

```typescript
// stores/auth-store.ts
interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  isLoading: boolean

  setAuth: (user: User, token: string) => void
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,

      setAuth: (user, token) => set({
        user,
        accessToken: token,
        isAuthenticated: true,
        isLoading: false
      }),

      logout: () => set({
        user: null,
        accessToken: null,
        isAuthenticated: false
      }),

      setUser: (user) => set({ user }),
    }),
    { name: 'auth-storage' }
  )
)
```

### 4.5 Composants Modifies

- `ArticleCard.tsx` - Ajoute bouton commentaires, utilise etat perso
- `VideoPanel.tsx` - Idem
- `Sidebar.tsx` - Ajoute lien profil, lien admin si role admin
- `TopBar.tsx` - Avatar user, menu dropdown

---

## 5. Securite

### 5.1 JWT Configuration

```
Access token:
- Expire: 15 minutes
- Stockage: memoire (state React)
- Contenu: user_id, role, email

Refresh token:
- Expire: 7 jours
- Stockage: HttpOnly cookie (Secure, SameSite=Strict)
- Rotation a chaque usage
- Blacklist en Redis lors du logout
```

### 5.2 OAuth Security

- State parameter anti-CSRF pour chaque flow
- Verification signature tokens providers
- Pas de stockage tokens OAuth cote client
- Tokens OAuth en DB chiffres (Fernet)

### 5.3 Protection Donnees

| Element | Methode |
|---------|---------|
| Passwords | Argon2 |
| Tokens OAuth DB | Fernet encryption |
| Rate limiting login | 5 tentatives / 15 min par IP |
| Validation inputs | Pydantic strict |

### 5.4 Headers Securite

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

---

## 6. RGPD

### 6.1 Principes Implementes

| Droit | Implementation |
|-------|----------------|
| Consentement | Table `user_consents`, opt-in explicite |
| Acces | Export JSON via `data_export_requests` |
| Rectification | Endpoint PATCH `/users/me` |
| Effacement | Soft delete 30j puis hard delete auto |
| Portabilite | Export JSON format standard |

### 6.2 Retention Policy

- Exports donnees: 7 jours puis suppression
- Comptes supprimes: soft delete 30 jours puis hard delete (Celery task)
- Logs audit: 1 an
- Refresh tokens expires: supprimes immediatement

### 6.3 Audit Logs

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    action VARCHAR(100),
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Resume Implementation

### Nouvelles Tables: 8
- users
- oauth_accounts
- user_article_states
- user_video_states
- user_keywords
- comments
- user_consents
- data_export_requests

### Tables Modifiees: 2
- user_config (ajoute user_id)
- keywords (permissions admin-only)

### Nouveaux Endpoints: ~35 routes

### Nouvelles Pages Frontend: 10+

### Estimation Complexite
- Backend auth + users: Medium
- Backend comments: Low-Medium
- Backend admin: Medium
- Frontend auth: Medium
- Frontend comments: Low-Medium
- Frontend admin: Medium-High
- Migrations DB: Low
- Tests: Medium

---

## 8. Questions Ouvertes

- [ ] Email service provider pour verification/reset? (SendGrid, Resend, etc.)
- [ ] Storage pour avatars? (S3, Cloudinary, local)
- [ ] Rate limiting implementation? (Redis, fastapi-limiter)

---

*Document valide le 2026-01-05*
