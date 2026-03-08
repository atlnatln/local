import React, { createContext, useContext, useReducer, useEffect, useCallback, ReactNode } from 'react';
import { tokenStorage } from '../utils/tokenStorage';
import { setAuthCookie, clearAuthCookie } from '../utils/authCookie';
import { navigateToNextJs } from '../utils/environment';
import {
  AUTH_CHANGE_EVENT,
  AUTH_STORAGE_KEYS,
  clearAuthSessionStorage,
  persistAuthSession,
  readSharedAuthState,
  readStoredUser,
} from '../utils/authSync';

// Enhanced error types for better error handling
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: string,
    public userMessage: string,
    public originalError?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Network error detection
const isNetworkError = (error: any): boolean => {
  return !error.response || error.code === 'NETWORK_ERROR' || error.name === 'TypeError';
};

const isCORSError = (error: any): boolean => {
  return error.message?.includes('CORS') || 
         error.message?.includes('cross-origin') ||
         (error.response?.status === 0 && !navigator.onLine === false);
};

// Safe localStorage utilities for test environment
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const safeLocalStorage = {
  getItem: (key: string): string | null => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage.getItem(key);
      }
    } catch (error) {
      // JSDOM/test environment error handling
      console.warn('localStorage getItem failed:', error);
    }
    return null;
  },
  
  setItem: (key: string, value: string): void => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(key, value);
      }
    } catch (error) {
      // JSDOM/test environment error handling
      console.warn('localStorage setItem failed:', error);
    }
  },
  
  removeItem: (key: string): void => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      // JSDOM/test environment error handling
      console.warn('localStorage removeItem failed:', error);
    }
  },
  
  clear: (): void => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.clear();
      }
    } catch (error) {
      // JSDOM/test environment error handling
      console.warn('localStorage clear failed:', error);
    }
  }
};

// Enhanced error normalization
const normalizeError = (error: any, context: string): APIError => {
  console.error(`[AUTH ERROR - ${context}]`, error);
  
  // Network/CORS errors
  if (isNetworkError(error)) {
    if (isCORSError(error)) {
      return new APIError(
        'CORS Error',
        0,
        'CORS_ERROR',
        'Güvenlik ayarları nedeniyle bağlantı kurulamadı. Lütfen daha sonra tekrar deneyin.',
        error
      );
    }
    return new APIError(
      'Network Error',
      0,
      'NETWORK_ERROR',
      'Bağlantı sorunu yaşanıyor. İnternet bağlantınızı kontrol edin.',
      error
    );
  }
  
  // HTTP errors
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data || {};
    
    switch (status) {
      case 400:
        // Backend'den gelen mesajı öncelikle kullan - non_field_errors dizisini de kontrol et
        let backendMessage = data.detail || data.message || data.error;
        
        // Django REST Framework non_field_errors formatını kontrol et
        if (!backendMessage && data.non_field_errors && Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
          backendMessage = data.non_field_errors[0];
        }
        
        // Backend 400 hata detaylarını safe log
        console.log('🔍 Backend 400 Error Status:', status);
        if (process.env.NODE_ENV === 'development') {
          console.log('🔍 Backend 400 Error Data (dev only):', data);
        }
        console.log('🔍 Extracted Backend Message:', backendMessage);
        return new APIError(
          'Bad Request',
          400,
          'VALIDATION_ERROR',
          backendMessage || 'Girilen bilgilerde hata var. Lütfen kontrol edin.',
          error
        );
      case 401:
        // Backend'den gelen mesajı öncelikle kullan
        const authMessage = data.detail || data.message || data.error;
        console.log('🔍 Backend 401 Error Status:', status);
        if (process.env.NODE_ENV === 'development') {
          console.log('🔍 Backend 401 Error Data (dev only):', data);
        }
        console.log('🔍 Extracted Auth Message:', authMessage);
        return new APIError(
          'Unauthorized',
          401,
          'AUTH_ERROR',
          authMessage || 'E-posta veya şifre hatalı.',
          error
        );
      case 403:
        return new APIError(
          'Forbidden',
          403,
          'PERMISSION_ERROR',
          'Bu işlem için yetkiniz bulunmuyor.',
          error
        );
      case 429:
        return new APIError(
          'Too Many Requests',
          429,
          'RATE_LIMIT_ERROR',
          'Çok fazla deneme yapıldı. Lütfen biraz bekleyin.',
          error
        );
      case 500:
        return new APIError(
          'Internal Server Error',
          500,
          'SERVER_ERROR',
          'Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.',
          error
        );
      default:
        return new APIError(
          'Unknown HTTP Error',
          status,
          'HTTP_ERROR',
          `Beklenmeyen hata oluştu (${status}). Lütfen tekrar deneyin.`,
          error
        );
    }
  }
  
  // Generic errors
  const errorMessage = error?.message || error?.detail || error?.userMessage || 'Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.';
  console.log('🔍 Generic Error Processing:', { error, extractedMessage: errorMessage });
  return new APIError(
    error.message || 'Unknown error',
    0,
    'UNKNOWN_ERROR',
    errorMessage,
    error
  );
};

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_email_verified?: boolean;
  is_active?: boolean;
  profile?: {
    created_at?: string;
    updated_at?: string;
  };
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: APIError | null;
  token: string | null;
  lastFetched: number | null; // Cache timestamp
  networkStatus: 'online' | 'offline' | 'unknown';
  lastErrorContext?: string;
}

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_FAILURE'; payload: { error: APIError; context: string } }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_NETWORK_STATUS'; payload: 'online' | 'offline' | 'unknown' };

// Initial state
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  token: null,
  lastFetched: null,
  networkStatus: 'unknown',
};

// Enhanced reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
        lastErrorContext: undefined,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        isLoading: false,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token,
        error: null,
        lastFetched: Date.now(),
        lastErrorContext: undefined,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        isLoading: false,
        isAuthenticated: false,
        user: null,
        token: null,
        error: action.payload.error,
        lastErrorContext: action.payload.context,
      };
    case 'LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        token: null,
        error: null,
        lastFetched: null,
        lastErrorContext: undefined,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
        lastErrorContext: undefined,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_NETWORK_STATUS':
      return {
        ...state,
        networkStatus: action.payload,
      };
    default:
      return state;
  }
}

// Enhanced context interface
const AuthContext = createContext<{
  state: AuthState;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (userData: any) => Promise<void>;
  clearError: () => void;
  checkAuthStatus: (forceRefresh?: boolean) => Promise<void>;
  // Helper methods for better UX
  isNetworkError: () => boolean;
  isAuthError: () => boolean;
  getErrorMessage: () => string;
} | null>(null);

// Provider Props
interface AuthProviderProps {
  children: ReactNode;
}

// Auth Provider Component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const getApiBaseUrl = useCallback(() => {
    if (typeof window !== 'undefined' && (window as any).WEBIMAR_API_BASE_URL) {
      return (window as any).WEBIMAR_API_BASE_URL as string;
    }

    if (typeof window !== 'undefined') {
      return `${window.location.origin}/api`;
    }

    return process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
  }, []);

  const finalizeLocalLogout = useCallback((reason: string, redirectToHome = true) => {
    tokenStorage.clearAll();
    clearAuthSessionStorage({ source: 'react', reason });

    try {
      clearAuthCookie();
    } catch (cookieErr) {
      console.warn('clearAuthCookie failed', cookieErr);
    }

    dispatch({ type: 'LOGOUT' });

    if (redirectToHome && typeof window !== 'undefined') {
      navigateToNextJs('/');
    }
  }, []);

  const persistVerifiedSession = useCallback((params: {
    accessToken: string;
    refreshToken?: string | null;
    user: User;
    reason: string;
  }) => {
    persistAuthSession({
      accessToken: params.accessToken,
      refreshToken: params.refreshToken,
      user: params.user,
      source: 'react',
      reason: params.reason,
    });

    try {
      setAuthCookie(params.user?.email);
    } catch (cookieErr) {
      console.warn('setAuthCookie failed', cookieErr);
    }

    dispatch({
      type: 'AUTH_SUCCESS',
      payload: {
        user: params.user,
        token: params.accessToken,
      },
    });
  }, []);

  const refreshAccessToken = useCallback(async () => {
    const refreshToken = tokenStorage.getRefreshToken();
    if (!refreshToken) {
      return null;
    }

    const response = await fetch(`${getApiBaseUrl()}/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    if (!data.access) {
      return null;
    }

    tokenStorage.setAccessToken(data.access);
    if (data.refresh) {
      tokenStorage.setRefreshToken(data.refresh);
    }

    return {
      accessToken: data.access as string,
      refreshToken: (data.refresh || refreshToken) as string,
    };
  }, [getApiBaseUrl]);

  // Network status monitoring
  useEffect(() => {
    const handleOnline = () => {
      console.log('🌐 Network: ONLINE');
      dispatch({ type: 'SET_NETWORK_STATUS', payload: 'online' });
    };
    
    const handleOffline = () => {
      console.log('🌐 Network: OFFLINE');
      dispatch({ type: 'SET_NETWORK_STATUS', payload: 'offline' });
    };

    // Set initial network status
    dispatch({ 
      type: 'SET_NETWORK_STATUS', 
      payload: navigator.onLine ? 'online' : 'offline' 
    });

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Mail/şifre girişi production'da devre dışı
  const login = async (email: string, password: string) => {
    dispatch({ type: 'AUTH_START' });

    try {
      console.warn('Mail/şifre login akışı devre dışı.', {
        email,
        attemptedPassword: Boolean(password),
      });

      throw new APIError(
        'Password login disabled',
        410,
        'GOOGLE_OAUTH_ONLY',
        'Mail/şifre girişi kapalı. Lütfen Google ile giriş yapın.'
      );
    } catch (error: any) {
      const normalizedError = normalizeError(error, 'LOGIN');
      console.error('🚨 Login error (normalized):', normalizedError);

      dispatch({
        type: 'AUTH_FAILURE',
        payload: {
          error: normalizedError,
          context: 'LOGIN'
        }
      });
      throw normalizedError;
    }
  };

  // Enhanced register function with comprehensive error handling
  const register = async (userData: any) => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
      
      console.log('🔄 Register attempt:', { 
        username: userData.username, 
        email: userData.email, 
        apiBase: API_BASE_URL 
      });
      
      const response = await fetch(`${API_BASE_URL}/accounts/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
          console.log('🚨 Register API Response Error Data:', errorData);
        } catch (parseError) {
          console.error('Failed to parse register error response:', parseError);
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        console.error('🚨 Register API error:', { status: response.status, data: errorData });
        
        // Rate limit hatası için özel mesaj
        if (response.status === 429) {
          const errorMessage = errorData.detail || errorData.message || 'Çok fazla kayıt denemesi yapıyorsunuz. Lütfen bir süre bekleyip tekrar deneyin.';
          const error = new Error(errorMessage);
          (error as any).response = { status: response.status, data: errorData };
          throw error;
        }
        
        // Backend'den gelen hata mesajını direkt kullan
        const backendErrorMessage = errorData.detail || errorData.message || errorData.error;
        const error = new Error(backendErrorMessage || `Registration failed with status ${response.status}`);
        (error as any).response = { status: response.status, data: errorData };
        throw error;
      }

      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const data = await response.json();
      console.log('✅ Registration successful, processing response...');
      
      // Admin onaylı sistemde kayıt sonrası kullanıcı authenticated olmamalı
      console.log('✅ Registration successful - Admin approval required');
      dispatch({ type: 'LOGOUT' }); // Kullanıcıyı çıkış yap
    } catch (error: any) {
      const normalizedError = normalizeError(error, 'REGISTER');
      console.error('🚨 Register error (normalized):', normalizedError);
      
      dispatch({ 
        type: 'AUTH_FAILURE', 
        payload: { 
          error: normalizedError, 
          context: 'REGISTER' 
        } 
      });
      throw normalizedError;
    }
  };

  // Logout function
  const logout = useCallback(async () => {
    try {
      const token = tokenStorage.getAccessToken();
      const refreshToken = tokenStorage.getRefreshToken();

      if (token) {
        await fetch(`${getApiBaseUrl()}/accounts/me/logout/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      }
    } catch (error) {
      console.error('Logout API hatası:', error);
    } finally {
      finalizeLocalLogout('manual-logout');
    }
  }, [finalizeLocalLogout, getApiBaseUrl]);

  // Clear error function
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Check auth status on app load (with caching)
  const checkAuthStatus = useCallback(async (forceRefresh = false) => {
    if (typeof window === 'undefined') {
      return;
    }

    let token = tokenStorage.getAccessToken();
    let refreshToken = tokenStorage.getRefreshToken();
    const sharedState = readSharedAuthState<User>();
    const sharedUser = readStoredUser<User>() || sharedState?.user || null;

    if (!token && !refreshToken) {
      if (state.isAuthenticated) {
        dispatch({ type: 'LOGOUT' });
      }
      return;
    }

    const CACHE_DURATION = 5 * 60 * 1000;
    const now = Date.now();

    if (!forceRefresh && state.lastFetched && state.user && (now - state.lastFetched < CACHE_DURATION)) {
      return;
    }

    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      if (!token && refreshToken) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          finalizeLocalLogout('refresh-failed', false);
          return;
        }

        token = refreshed.accessToken;
        refreshToken = refreshed.refreshToken;
      }

      if (!token) {
        finalizeLocalLogout('missing-access-token', false);
        return;
      }

      let response = await fetch(`${getApiBaseUrl()}/accounts/me/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.status === 401 && refreshToken) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          finalizeLocalLogout('refresh-failed', false);
          return;
        }

        token = refreshed.accessToken;
        refreshToken = refreshed.refreshToken;
        response = await fetch(`${getApiBaseUrl()}/accounts/me/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }

      if (!response.ok) {
        if (response.status === 401) {
          finalizeLocalLogout('session-expired', false);
          return;
        }

        if (sharedUser && token) {
          dispatch({
            type: 'AUTH_SUCCESS',
            payload: {
              user: sharedUser,
              token,
            },
          });
          return;
        }

        finalizeLocalLogout('session-invalid', false);
        return;
      }

      const userData = await response.json();
      persistVerifiedSession({
        accessToken: token,
        refreshToken,
        user: userData,
        reason: forceRefresh ? 'forced-auth-check' : 'auth-check',
      });
    } catch (error) {
      if (state.user && token) {
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: {
            user: state.user,
            token,
          },
        });
      } else if (sharedUser && token) {
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: {
            user: sharedUser,
            token,
          },
        });
      } else {
        finalizeLocalLogout('network-auth-check-failed', false);
      }
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [finalizeLocalLogout, getApiBaseUrl, persistVerifiedSession, refreshAccessToken, state.isAuthenticated, state.lastFetched, state.user]);

  useEffect(() => {
    const syncAuthSignal = async () => {
      const sharedState = readSharedAuthState<User>();
      const accessToken = tokenStorage.getAccessToken();

      if (!sharedState) {
        return;
      }

      if (!sharedState.isAuthenticated) {
        if (state.isAuthenticated || accessToken || tokenStorage.getRefreshToken()) {
          finalizeLocalLogout(sharedState.reason || 'external-logout');
        }
        return;
      }

      if (accessToken) {
        await checkAuthStatus(true);
      }
    };

    const handleStorage = (event: StorageEvent) => {
      if (!event.key || Object.values(AUTH_STORAGE_KEYS).includes(event.key as typeof AUTH_STORAGE_KEYS[keyof typeof AUTH_STORAGE_KEYS])) {
        void syncAuthSignal();
      }
    };

    const handleAuthChange = () => {
      void syncAuthSignal();
    };

    window.addEventListener('storage', handleStorage);
    window.addEventListener(AUTH_CHANGE_EVENT, handleAuthChange as EventListener);

    return () => {
      window.removeEventListener('storage', handleStorage);
      window.removeEventListener(AUTH_CHANGE_EVENT, handleAuthChange as EventListener);
    };
  }, [checkAuthStatus, finalizeLocalLogout, state.isAuthenticated]);

  // App başladığında auth durumunu kontrol et
  useEffect(() => {
    void checkAuthStatus();
  }, [checkAuthStatus]);

  // Helper methods for better UX
  const isNetworkError = (): boolean => {
    return state.error?.code === 'NETWORK_ERROR' || state.error?.code === 'CORS_ERROR';
  };

  const isAuthError = (): boolean => {
    return state.error?.code === 'AUTH_ERROR' || state.error?.status === 401;
  };

  const getErrorMessage = (): string => {
    if (!state.error) return '';
    
    // Network durumuna göre özelleştirilmiş mesajlar
    if (state.networkStatus === 'offline') {
      return 'İnternet bağlantınız kesildi. Lütfen bağlantınızı kontrol edin.';
    }
    
    return state.error.userMessage || state.error.message || 'Beklenmeyen bir hata oluştu.';
  };

  const contextValue = {
    state,
    login,
    logout,
    register,
    clearError,
    checkAuthStatus,
    isNetworkError,
    isAuthError,
    getErrorMessage,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
