// Admin types for admin panel

export interface AdminUser {
  id: number;
  email: string;
  username: string;
  display_name?: string;
  avatar_url?: string;
  bio?: string;
  is_active: boolean;
  is_admin: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AdminUserUpdate {
  is_active?: boolean;
  is_admin?: boolean;
  email?: string;
  username?: string;
}

export interface AdminComment {
  id: number;
  content: string;
  target_type: 'article' | 'video';
  target_id: number;
  parent_id?: number;
  author: {
    id: number;
    username: string;
    display_name?: string;
    avatar_url?: string;
  };
  author_email: string;
  is_edited: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  hasMore: boolean;
  offset: number;
  limit: number;
}

export interface ScrapingRun {
  task_id: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  source_type: string;
  articles_scraped: number;
  articles_saved: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

export interface ScrapingStats {
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  total_articles_scraped: number;
  total_articles_saved: number;
  success_rate: number;
}

export interface AdminStats {
  users: {
    total: number;
    active: number;
    admins: number;
  };
  content: {
    articles: number;
    videos: number;
    comments: number;
  };
  scraping: ScrapingStats;
}

export interface AdminUsersFilters {
  search?: string;
  is_active?: boolean;
  is_admin?: boolean;
  limit?: number;
  offset?: number;
}

export interface AdminCommentsFilters {
  search?: string;
  is_deleted?: boolean;
  limit?: number;
  offset?: number;
}
