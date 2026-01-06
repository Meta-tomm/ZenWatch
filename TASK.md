# Task: Frontend - Auth Store, Hooks, Components, Pages

## Branch: feature/auth-frontend

## Objectif
Creer le frontend React/Next.js pour l'authentification et les commentaires.

## Stack
- Next.js 14 (App Router)
- TypeScript
- TailwindCSS + shadcn/ui
- Zustand (state)
- TanStack Query
- Axios

## Composants shadcn a installer si manquants
```bash
cd frontend
npx shadcn@latest add avatar dropdown-menu textarea form
```

## Fichiers a creer

### 1. Types (`frontend/types/auth.ts`)
```typescript
export interface User {
  id: string
  email: string
  username: string
  avatar_url?: string
  bio?: string
  github_url?: string
  portfolio_url?: string
  role: 'user' | 'admin'
  is_verified: boolean
  created_at: string
}

export interface LoginRequest { email: string; password: string }
export interface RegisterRequest { email: string; username: string; password: string }
export interface AuthTokens { access_token: string; token_type: string }

export interface Comment {
  id: number
  user_id: string
  user?: UserPublicProfile
  article_id?: number
  video_id?: number
  parent_id?: number
  content: string
  is_deleted: boolean
  created_at: string
  replies?: Comment[]
}

export interface UserPublicProfile {
  id: string
  username: string
  avatar_url?: string
  bio?: string
  github_url?: string
  portfolio_url?: string
}
```

### 2. Auth Store (`frontend/stores/auth-store.ts`)
- user, accessToken, isAuthenticated, isLoading
- setAuth, logout, setUser, setLoading

### 3. API Client (`frontend/lib/api-client.ts`)
Ajouter:
- authApi: login, register, logout, refresh, getMe, oauthRedirect
- commentsApi: getForArticle, getForVideo, create, update, delete
- userKeywordsApi: list, create, delete

### 4. Hooks (`frontend/hooks/`)
- `useAuth.ts` - login, register, logout, loginWithOAuth
- `useCurrentUser.ts` - user depuis store
- `useComments.ts` - useQuery + mutations
- `useUserKeywords.ts` - CRUD

### 5. Components Auth (`frontend/components/auth/`)
- `LoginForm.tsx` - Form email/password + validation zod
- `RegisterForm.tsx` - Form inscription
- `OAuthButtons.tsx` - Boutons GitHub, Google, Discord
- `AuthGuard.tsx` - Protection routes

### 6. Components Comments (`frontend/components/comments/`)
- `CommentSection.tsx` - Container article/video
- `CommentThread.tsx` - Recursif avec reponses
- `CommentForm.tsx` - Nouveau commentaire
- `CommentCard.tsx` - Un commentaire + actions

### 7. Components Profile (`frontend/components/profile/`)
- `ProfileCard.tsx` - Profil public
- `ProfileEditForm.tsx` - Edition profil

### 8. Pages (`frontend/app/`)
```
app/
├── (auth)/
│   ├── layout.tsx        # Layout sans sidebar
│   ├── login/page.tsx
│   └── register/page.tsx
├── profile/
│   ├── page.tsx          # Mon profil
│   └── [username]/page.tsx
├── settings/
│   └── page.tsx
```

## Verification
```bash
npm run build
npm run lint
```

## Commit final
```
feat(frontend): add auth pages and comment components
```
