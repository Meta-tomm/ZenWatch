// frontend/types/index.ts

export interface Article {
  id: string;
  title: string;
  url: string;
  content?: string;
  summary?: string;
  author?: string;
  published_at: string;
  scraped_at?: string;
  score: number;
  category: string;
  tags: string[];
  language?: string;
  read_time_minutes?: number;
  thumbnail_url?: string;
  video_url?: string;
  upvotes: number;
  comments_count: number;
  is_read: boolean;
  is_favorite: boolean;
  is_archived: boolean;
  is_bookmarked: boolean;
  is_dismissed: boolean;
  is_liked?: boolean;
  is_disliked?: boolean;
  bookmarked_at?: string;
  source_type: string;
  created_at: string;
  updated_at?: string;
  likes?: number;
  dislikes?: number;
  user_reaction?: 'like' | 'dislike' | null;
}

export interface Video {
  id: string;
  title: string;
  url: string;
  video_url: string;
  thumbnail_url?: string;
  video_id?: string;
  platform: 'youtube' | 'vimeo' | 'other';
  summary?: string;
  author?: string;
  published_at: string;
  score: number;
  category: string;
  tags: string[];
  duration_minutes?: number;
  views?: number;
  likes?: number;
  dislikes?: number;
  is_favorite: boolean;
  is_bookmarked: boolean;
  is_dismissed: boolean;
  bookmarked_at?: string;
  source_type: string;
  created_at: string;
  updated_at?: string;
  user_reaction?: 'like' | 'dislike' | null;
}

export interface Keyword {
  id: string;
  keyword: string;
  category: string;
  weight: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Source {
  id: string;
  name: string;
  type: string;
  base_url?: string;
  is_active: boolean;
  scrape_frequency_hours: number;
  last_scraped_at?: string;
  config: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface UserConfig {
  id: string;
  email: string;
  daily_digest_enabled: boolean;
  digest_time?: string;
  min_score_threshold: number;
  preferred_categories: string[];
  email_frequency: 'daily' | 'weekly';
  created_at: string;
  updated_at?: string;
}

export interface ArticleFilters {
  search?: string;
  categories?: string[];
  sources?: string[];
  sort?: 'score' | 'date' | 'popularity';
  timeRange?: 'all' | '24h' | '7d' | '30d';
  minScore?: number;
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  hasMore: boolean;
  offset?: number;
  limit?: number;
}

export type Theme = 'light' | 'dark' | 'zenwatch';

// Library & Triage types
export interface LibraryResponse {
  items: Article[];
  total: number;
  unread_count: number;
}

export interface TriageResponse {
  items: Article[];
  remaining_count: number;
}

export type LibraryFilter = 'all' | 'articles' | 'videos';
export type LibraryView = 'list' | 'grid';

// Analytics types
export interface Trend {
  id: number;
  keyword: string;
  category?: string;
  trend_score: number;
  article_count: number;
  date: string;
  created_at: string;
}

export interface AnalyticsSummary {
  total_articles: number;
  total_sources: number;
  total_keywords: number;
  avg_score_last_7_days: number;
  top_trends: Trend[];
  articles_by_category: Record<string, number>;
  articles_scraped_today: number;
}
