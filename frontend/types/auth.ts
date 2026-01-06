// frontend/types/auth.ts

export interface User {
  id: string;
  email: string;
  username: string;
  avatar_url?: string;
  bio?: string;
  github_url?: string;
  portfolio_url?: string;
  role: 'user' | 'admin';
  is_verified: boolean;
  created_at: string;
}

export interface UserPublicProfile {
  id: string;
  username: string;
  avatar_url?: string;
  bio?: string;
  github_url?: string;
  portfolio_url?: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface Comment {
  id: number;
  user_id: string;
  user?: UserPublicProfile;
  article_id?: number;
  video_id?: number;
  parent_id?: number;
  content: string;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  replies?: Comment[];
}

export interface CreateCommentRequest {
  content: string;
  article_id?: number;
  video_id?: number;
  parent_id?: number;
}

export interface UpdateCommentRequest {
  content: string;
}

export interface UserKeyword {
  id: number;
  user_id: string;
  keyword: string;
  weight: number;
  created_at: string;
}

export interface CreateUserKeywordRequest {
  keyword: string;
  weight?: number;
}

export type OAuthProvider = 'github' | 'google' | 'discord';
