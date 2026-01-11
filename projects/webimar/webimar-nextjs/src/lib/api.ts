import axios from 'axios';
import type { StructureCategoriesResponse, SEOMetaResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config: any) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error: any) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: any) => {
    return response;
  },
  (error: any) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Get structure categories for homepage SSR
  async getStructureCategories(): Promise<StructureCategoriesResponse> {
    const response = await apiClient.get<StructureCategoriesResponse>('/calculations/structure-categories/');
    return response.data;
  },

  // Get SEO meta data for homepage
  async getSEOMetaData(): Promise<SEOMetaResponse> {
    const response = await apiClient.get<SEOMetaResponse>('/calculations/seo-meta/');
    return response.data;
  },

  // Health check
  async healthCheck(): Promise<{ status: string; app: string; message: string }> {
    const response = await apiClient.get('/calculations/health/');
    return response.data;
  },
};

export default apiClient;
