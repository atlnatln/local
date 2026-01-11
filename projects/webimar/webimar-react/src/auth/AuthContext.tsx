import React, { createContext, useContext, useReducer, useEffect, useCallback, ReactNode } from 'react';
import { tokenStorage } from '../utils/tokenStorage';
import { setAuthCookie, clearAuthCookie } from '../utils/authCookie';
import { replaceToNextJs, navigateToNextJs } from '../utils/environment';

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
  logout: () => void;
  register: (userData: any) => Promise<void>;
  clearError: () => void;
  checkAuthStatus: (forceRefresh?: boolean) => void;
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

  // Enhanced login function with comprehensive error handling
  const login = async (email: string, password: string) => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
      
      console.log('🔄 Login attempt:', { email, apiBase: API_BASE_URL });
      
      const response = await fetch(`${API_BASE_URL}/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: email, password }),
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
          console.log('🚨 Login API Response Error Data:', errorData);
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        console.error('🚨 Login API error:', { status: response.status, data: errorData });
        
        // Backend'den gelen hata mesajını detaylı debug
        console.log('🔍 ERROR DATA STRUCTURE:', {
          errorData,
          detail: errorData.detail,
          message: errorData.message,
          error: errorData.error,
          nonFieldErrors: errorData.non_field_errors
        });
        
        // Backend'den gelen hata mesajını direkt kullan
        const backendErrorMessage = errorData.detail || 
                                   errorData.message || 
                                   errorData.error || 
                                   (Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors);
        console.log('🔍 FINAL BACKEND MESSAGE:', backendErrorMessage);
        
        const error = new Error(backendErrorMessage || `Login failed with status ${response.status}`);
        (error as any).response = { status: response.status, data: errorData };
        throw error;
      }

      const data = await response.json();
      console.log('✅ Login successful, fetching user data...');
      
      // Token'ı localStorage'a kaydet
      tokenStorage.setAccessToken(data.access);
      tokenStorage.setRefreshToken(data.refresh);
      
      // User bilgilerini al
      const userResponse = await fetch(`${API_BASE_URL}/accounts/me/`, {
        headers: {
          'Authorization': `Bearer ${data.access}`,
        },
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        console.log('✅ User data fetched successfully');
        
        // Token'ları ve user bilgilerini localStorage'a kaydet
        tokenStorage.setUser(userData);
        
        // --- CRITICAL: Cross-app key compatibility ---
        try {
          // Next.js uygulamasının kontrol ettiği anahtar isimlerini de set et
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('refresh_token', data.refresh);
          localStorage.setItem('token', data.access);
          localStorage.setItem('user', JSON.stringify(userData));
        } catch (e) {
          console.warn('localStorage write failed:', e);
        }

        // Shared auth state (mevcut uygulamalar kontrol ediyor)
        try {
          const authState = {
            isAuthenticated: true,
            user: userData,
            timestamp: Date.now()
          };
          localStorage.setItem('webimar_auth_state', JSON.stringify(authState));
        } catch (e) {
          console.warn('webimar_auth_state write failed:', e);
        }
        // ----------------------------------------------
        
        // Next.js header görünürlüğü için auth cookie ayarla
        try { setAuthCookie(userData?.email); } catch (cookieErr) { console.warn('setAuthCookie failed', cookieErr); }
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: {
            user: userData,
            token: data.access,
          },
        });
        
        console.log('🔄 [React] Auth state updated - login successful');
        
        // Login başarılı - önceki sayfaya veya ana sayfaya yönlendir
        const returnUrl = localStorage.getItem('returnUrl') || sessionStorage.getItem('returnUrl');
        localStorage.removeItem('returnUrl');
        sessionStorage.removeItem('returnUrl');
        
        // Gecikmeli yönlendirme: storage write işlemlerinin tarayıcıda commit olmasına kısa süre izin ver
        setTimeout(() => {
          if (returnUrl && returnUrl !== '/login' && returnUrl !== '/register') {
            window.location.replace(returnUrl);
          } else {
            replaceToNextJs('/');
          }
        }, 120); // 100-200ms arası küçük gecikme yarışmayı azaltır
      } else {
        console.error('🚨 Failed to fetch user data:', userResponse.status);
        const userError = new Error('Kullanıcı bilgileri alınamadı');
        (userError as any).response = { status: userResponse.status };
        throw userError;
      }
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
  const logout = async () => {
    try {
      const token = tokenStorage.getAccessToken();
      if (token) {
        // Backend'e logout isteği gönder
        const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
        await fetch(`${API_BASE_URL}/accounts/me/logout/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout API hatası:', error);
    } finally {
      // Shared auth state - logout bildirimi
      const authState = {
        isAuthenticated: false,
        user: null,
        timestamp: Date.now()
      };
      
      // Token storage temizle
      tokenStorage.clearAll();
      
      // Hem React hem Next'in kontrol ettiği anahtarları temizle
      try {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token');
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      } catch (e) {
        console.warn('localStorage remove failed:', e);
      }
      
      try {
        localStorage.setItem('webimar_auth_state', JSON.stringify(authState));
      } catch (e) {
        console.warn('webimar_auth_state clear failed:', e);
      }
      
      // Next.js ile senkron: auth cookie'lerini temizle
      try { clearAuthCookie(); } catch (cookieErr) { console.warn('clearAuthCookie failed', cookieErr); }
      
      dispatch({ type: 'LOGOUT' });
      
      console.log('� [React] Auth state cleared - redirecting');
      
      // Direkt yönlendirme
      navigateToNextJs('/');
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Check auth status on app load (with caching)
  const checkAuthStatus = useCallback(async (forceRefresh = false) => {
    if (typeof window === 'undefined') {
      return;
    }
    
    const token = tokenStorage.getAccessToken();
    
    if (!token) {
      return;
    }

    // Cache kontrolü: son fetch'ten bu yana 5 dakika geçtiyse veya force refresh
    const CACHE_DURATION = 5 * 60 * 1000; // 5 dakika
    const now = Date.now();
    
    if (!forceRefresh && state.lastFetched && state.user && (now - state.lastFetched < CACHE_DURATION)) {
      // Cache fresh, API call yapmaya gerek yok
      return;
    }

    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_BASE_URL}/accounts/me/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        
        // User bilgilerini localStorage'a kaydet
        tokenStorage.setUser(userData);
        
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: {
            user: userData,
            token,
          },
        });
        // Cookie'yi tazele (süre uzasın)
        try { setAuthCookie(userData?.email); } catch {}
      } else {
        // Token geçersiz, temizle
        tokenStorage.clearAll();
        try { clearAuthCookie(); } catch {}
        dispatch({ type: 'LOGOUT' });
      }
    } catch (error) {
      tokenStorage.clearAll();
      try { clearAuthCookie(); } catch {}
      dispatch({ type: 'LOGOUT' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [state.lastFetched, state.user]);

  // App başladığında auth durumunu kontrol et
  useEffect(() => {
    checkAuthStatus();
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
