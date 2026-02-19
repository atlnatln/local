// API Service for Webimar Calculation Endpoints
import axios from 'axios';
import { tokenStorage } from '../utils/tokenStorage';
import { CalculationResult, StructureType, STRUCTURE_TYPE_TO_ID } from '../types';

console.log('🔧 API SERVICE FILE LOADING - DYNAMIC VERSION 2.0');

// Dynamic URL resolver function - always check window at runtime
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined' && (window as any).WEBIMAR_API_BASE_URL) {
    return (window as any).WEBIMAR_API_BASE_URL;
  }
  return 'http://localhost:8000/api';
};

// Export getter for external use if needed
export const API_BASE_URL = getApiBaseUrl(); 

const api = axios.create({
  // baseURL intentionally omitted to force dynamic resolution in interceptor
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token AND set dynamic baseURL
api.interceptors.request.use(
  (config) => {
    // Set baseURL dynamically for every request
    config.baseURL = getApiBaseUrl();
    
    // Debug log to confirm correct URL is being used
    // console.log(`🔧 Request to ${config.url} using baseURL: ${config.baseURL}`);

    const token = tokenStorage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling auth errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const original = error.config;

    // Local docker fallback: if 8000 is down, try 8001 once
    const isNetworkError = !error.response;
    const currentBaseUrl = original?.baseURL || getApiBaseUrl();
    const isLocal8000 = typeof currentBaseUrl === 'string' &&
      (currentBaseUrl.includes('http://localhost:8000') || currentBaseUrl.includes('http://127.0.0.1:8000'));

    if (isNetworkError && isLocal8000 && !original._baseUrlRetry) {
      original._baseUrlRetry = true;
      const fallbackBase = currentBaseUrl.replace('localhost:8000', 'localhost:8001').replace('127.0.0.1:8000', 'localhost:8001');
      if (typeof window !== 'undefined') {
        (window as any).WEBIMAR_API_BASE_URL = fallbackBase;
      }
      original.baseURL = fallbackBase;
      return api(original);
    }

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      try {
        const refreshToken = tokenStorage.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Use dynamic URL for refresh token too
        const currentBaseUrl = getApiBaseUrl();
        const response = await axios.post(`${currentBaseUrl}/token/refresh/`, {
          refresh: refreshToken
        });

        const { access } = response.data;
        tokenStorage.setAccessToken(access);

        original.headers.Authorization = `Bearer ${access}`;
        // Update baseURL for retry as well
        original.baseURL = currentBaseUrl;
        return api(original);
      } catch (refreshError) {
        tokenStorage.clearAll();
        window.location.href = '/giris';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export { api };

// Structure calculation functions
export const calculateBagEvi = async (data: any): Promise<CalculationResult> => {
  try {
    const response = await api.post('/calculations/bag-evi/', data);
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

export const calculateSera = async (data: any): Promise<CalculationResult> => {
  try {
    const response = await api.post('/calculations/sera/', data);
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

export const calculateHayvancilik = async (data: any): Promise<CalculationResult> => {
  try {
    const response = await api.post('/calculations/hayvancilik/', data);
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

export const calculateDepoAmbar = async (data: any): Promise<CalculationResult> => {
  try {
    const response = await api.post('/calculations/depo-ambar/', data);
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

// Generic calculation function for new endpoints
export const calculateStructure = async (structureType: StructureType, data: any): Promise<CalculationResult> => {
  // Validate structure type
  if (!STRUCTURE_TYPE_TO_ID[structureType]) {
    throw new Error(`Unsupported structure type: ${structureType}`);
  }

  try {
    // Use the structureType slug directly as the endpoint
    const response = await api.post(`/calculations/${structureType}/`, data);
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

export const trackPublicCalculation = async (data: {
  event_type: 'calculation';
  calculation_type: string;
  calculation_data: Record<string, unknown>;
  result_data: Record<string, unknown>;
  location_data: Record<string, unknown>;
}) => {
  try {
    const response = await api.post('/calculations/public-track/', data);
    return response.data;
  } catch (error) {
    console.error('Public calculation tracking failed:', error);
    throw error;
  }
};

export const submitCalculationFeedback = async (data: {
  message: string;
  calculation_type: string;
  source_app: 'react-spa' | 'nextjs-pages';
  page_path: string;
}) => {
  const response = await api.post('/calculations/feedback/', data);
  return response.data;
};

// History management
export const saveCalculationHistory = async (data: any) => {
  try {
    return await api.post('/history/', data);
  } catch (error) {
    console.error('Failed to save calculation history:', error);
    throw error;
  }
};

export const getCalculationHistory = async () => {
  try {
    const response = await api.get('/history/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch calculation history:', error);
    throw error;
  }
};

export const deleteCalculationHistory = async (id: number) => {
  try {
    return await api.delete(`/history/${id}/`);
  } catch (error) {
    console.error('Failed to delete calculation history:', error);
    throw error;
  }
};

// User profile
export const getUserProfile = async () => {
  try {
    const response = await api.get('/auth/profile/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch user profile:', error);
    throw error;
  }
};

export const updateUserProfile = async (data: any) => {
  try {
    const response = await api.put('/auth/profile/', data);
    return response.data;
  } catch (error) {
    console.error('Failed to update user profile:', error);
    throw error;
  }
};

// Authentication
export const loginUser = async (email: string, password: string) => {
  try {
    const response = await api.post('/auth/login/', { email, password });
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

export const registerUser = async (data: any) => {
  try {
    const response = await api.post('/auth/register/', data);
    return response.data;
  } catch (error) {
    console.error('Registration failed:', error);
    throw error;
  }
};

export const logoutUser = async () => {
  try {
    const refreshToken = tokenStorage.getRefreshToken();
    if (refreshToken) {
      await api.post('/auth/logout/', { refresh: refreshToken });
    }
  } catch (error) {
    console.error('Logout failed:', error);
  } finally {
    tokenStorage.clearAll();
  }
};

// Password reset
export const requestPasswordReset = async (email: string) => {
  try {
    const response = await api.post('/auth/password-reset/', { email });
    return response.data;
  } catch (error) {
    console.error('Password reset request failed:', error);
    throw error;
  }
};

export const confirmPasswordReset = async (token: string, password: string) => {
  try {
    const response = await api.post('/auth/password-reset/confirm/', { token, password });
    return response.data;
  } catch (error) {
    console.error('Password reset confirmation failed:', error);
    throw error;
  }
};

export default api;
