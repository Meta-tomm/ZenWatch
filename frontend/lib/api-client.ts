import axios from 'axios';
import type { Article, Keyword, Source, UserConfig, ArticleFilters, PaginatedResponse } from '@/types';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Articles API
export const articlesApi = {
  getArticles: async (params: ArticleFilters): Promise<PaginatedResponse<Article>> => {
    const response = await apiClient.get('/articles', { params });
    return response.data;
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
};

// Keywords API
export const keywordsApi = {
  getKeywords: async (): Promise<Keyword[]> => {
    const response = await apiClient.get('/keywords');
    return response.data;
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

  triggerScraping: async (sources?: string[]): Promise<{ task_id: string }> => {
    const response = await apiClient.post('/scraping/trigger', { sources });
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
