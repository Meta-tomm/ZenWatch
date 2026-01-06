import axios from 'axios';
import type { Article, Video, Keyword, Source, UserConfig, ArticleFilters, PaginatedResponse } from '@/types';
import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthTokens,
  Comment,
  CommentCreate,
  CommentUpdate,
  UserKeyword,
  UserKeywordCreate,
  ProfileUpdate,
  UserPublicProfile,
} from '@/types/auth';
import { useAuthStore } from '@/store/auth-store';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add Authorization header
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 - token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/auth/refresh`,
          {},
          { withCredentials: true }
        );

        const { access_token } = response.data;
        const { setAuth, user } = useAuthStore.getState();

        if (user) {
          setAuth(user, access_token);
        }

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch {
        useAuthStore.getState().logout();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }

    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Articles API
export const articlesApi = {
  getArticles: async (params: ArticleFilters): Promise<PaginatedResponse<Article>> => {
    // Convert arrays to comma-separated strings for backend
    const queryParams: Record<string, any> = {
      ...params,
      categories: params.categories?.length ? params.categories.join(',') : undefined,
      sources: params.sources?.length ? params.sources.join(',') : undefined,
      timeRange: params.timeRange === 'all' ? undefined : params.timeRange,
    };

    // Remove undefined values
    Object.keys(queryParams).forEach(key => {
      if (queryParams[key] === undefined) {
        delete queryParams[key];
      }
    });

    const response = await apiClient.get('/articles', { params: queryParams });

    // Transform backend response to match frontend types
    const data = response.data;
    return {
      data: data.data.map((article: any) => ({
        ...article,
        id: String(article.id), // Convert ID to string
        tags: article.tags || [], // Ensure tags is always an array
      })),
      total: data.total,
      hasMore: data.hasMore,
    };
  },

  toggleFavorite: async (id: string): Promise<Article> => {
    const response = await apiClient.patch(`/articles/${id}/favorite`);
    return response.data;
  },

  markRead: async (id: string): Promise<Article> => {
    const response = await apiClient.patch(`/articles/${id}/read`);
    return response.data;
  },

  archive: async (id: string): Promise<Article> => {
    const response = await apiClient.patch(`/articles/${id}/archive`);
    return response.data;
  },

  addNote: async (id: string, note: string): Promise<Article> => {
    const response = await apiClient.post(`/articles/${id}/notes`, { note });
    return response.data;
  },

  getBestOfWeek: async (): Promise<Article | null> => {
    const response = await apiClient.get('/articles/best-of-week');
    return response.data;
  },

  toggleLike: async (id: string): Promise<Article> => {
    const response = await apiClient.post(`/articles/${id}/like`);
    return response.data;
  },

  toggleDislike: async (id: string): Promise<Article> => {
    const response = await apiClient.post(`/articles/${id}/dislike`);
    return response.data;
  },
};

// Videos API
export const videosApi = {
  getVideos: async (params?: ArticleFilters): Promise<PaginatedResponse<Video>> => {
    const queryParams: Record<string, any> = {
      ...params,
      categories: params?.categories?.length ? params.categories.join(',') : undefined,
      sources: params?.sources?.length ? params.sources.join(',') : undefined,
      timeRange: params?.timeRange === 'all' ? undefined : params?.timeRange,
    };

    Object.keys(queryParams).forEach(key => {
      if (queryParams[key] === undefined) {
        delete queryParams[key];
      }
    });

    const response = await apiClient.get('/videos', { params: queryParams });
    const data = response.data;
    return {
      data: data.data.map((video: any) => ({
        ...video,
        id: String(video.id),
        tags: video.tags || [],
      })),
      total: data.total,
      hasMore: data.hasMore,
    };
  },

  getBestOfWeek: async (): Promise<Video | null> => {
    const response = await apiClient.get('/videos/best-of-week');
    return response.data;
  },

  toggleFavorite: async (id: string): Promise<Video> => {
    const response = await apiClient.patch(`/videos/${id}/favorite`);
    return response.data;
  },

  toggleLike: async (id: string): Promise<Video> => {
    const response = await apiClient.post(`/videos/${id}/like`);
    return response.data;
  },

  toggleDislike: async (id: string): Promise<Video> => {
    const response = await apiClient.post(`/videos/${id}/dislike`);
    return response.data;
  },
};

// Keywords API
export const keywordsApi = {
  getKeywords: async (): Promise<Keyword[]> => {
    const response = await apiClient.get('/keywords');
    return response.data.keywords;
  },

  createKeyword: async (data: Partial<Keyword>): Promise<Keyword> => {
    const response = await apiClient.post('/keywords', data);
    return response.data;
  },

  updateKeyword: async (id: string, data: Partial<Keyword>): Promise<Keyword> => {
    const response = await apiClient.put(`/keywords/${id}`, data);
    return response.data;
  },

  deleteKeyword: async (id: string): Promise<void> => {
    await apiClient.delete(`/keywords/${id}`);
  },
};

// Sources API
export const sourcesApi = {
  getSources: async (): Promise<Source[]> => {
    const response = await apiClient.get('/sources');
    return response.data;
  },

  updateSource: async (id: string, data: Partial<Source>): Promise<Source> => {
    const response = await apiClient.put(`/sources/${id}`, data);
    return response.data;
  },

  triggerScraping: async (sources?: string[]): Promise<{ task_id: string; status: string; message: string }> => {
    const response = await apiClient.post('/scraping/trigger', { sources });
    return response.data;
  },

  getScrapingStatus: async (taskId: string): Promise<{
    task_id: string;
    status: string;
    source_type: string;
    articles_scraped: number;
    articles_saved: number;
    error_message?: string;
  }> => {
    const response = await apiClient.get(`/scraping/status/${taskId}`);
    return response.data;
  },
};

// User Config API
export const userConfigApi = {
  getConfig: async (): Promise<UserConfig> => {
    const response = await apiClient.get('/user/config');
    return response.data;
  },

  updateConfig: async (data: Partial<UserConfig>): Promise<UserConfig> => {
    const response = await apiClient.put('/user/config', data);
    return response.data;
  },
};

// Auth API
export const authApi = {
  login: async (data: LoginRequest): Promise<{ user: User; tokens: AuthTokens }> => {
    const response = await apiClient.post('/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<{ user: User; tokens: AuthTokens }> => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  refresh: async (): Promise<AuthTokens> => {
    const response = await apiClient.post('/auth/refresh', {}, { withCredentials: true });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  oauthRedirect: (provider: 'github' | 'google' | 'discord'): string => {
    return `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/auth/oauth/${provider}`;
  },

  updateProfile: async (data: ProfileUpdate): Promise<User> => {
    const response = await apiClient.patch('/auth/profile', data);
    return response.data;
  },

  getPublicProfile: async (username: string): Promise<UserPublicProfile> => {
    const response = await apiClient.get(`/users/${username}`);
    return response.data;
  },
};

// Comments API
export const commentsApi = {
  getForArticle: async (articleId: number): Promise<Comment[]> => {
    const response = await apiClient.get(`/articles/${articleId}/comments`);
    return response.data;
  },

  getForVideo: async (videoId: number): Promise<Comment[]> => {
    const response = await apiClient.get(`/videos/${videoId}/comments`);
    return response.data;
  },

  create: async (data: CommentCreate): Promise<Comment> => {
    const response = await apiClient.post('/comments', data);
    return response.data;
  },

  update: async (id: number, data: CommentUpdate): Promise<Comment> => {
    const response = await apiClient.patch(`/comments/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/comments/${id}`);
  },
};

// User Keywords API
export const userKeywordsApi = {
  list: async (): Promise<UserKeyword[]> => {
    const response = await apiClient.get('/user/keywords');
    return response.data;
  },

  create: async (data: UserKeywordCreate): Promise<UserKeyword> => {
    const response = await apiClient.post('/user/keywords', data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/user/keywords/${id}`);
  },
};
