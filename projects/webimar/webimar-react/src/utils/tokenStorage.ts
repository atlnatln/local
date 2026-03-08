import { AUTH_STORAGE_KEYS, dispatchAuthChange } from './authSync';

// Token management constants - Next.js ile uyumlu key'ler
export const TOKEN_KEYS = {
  ACCESS_TOKEN: AUTH_STORAGE_KEYS.ACCESS_TOKEN,
  REFRESH_TOKEN: AUTH_STORAGE_KEYS.REFRESH_TOKEN,
  TOKEN: AUTH_STORAGE_KEYS.TOKEN,
  USER: AUTH_STORAGE_KEYS.USER,
} as const;

const emitAuthChange = (reason: string) => {
  dispatchAuthChange({
    isAuthenticated: Boolean(localStorage.getItem(TOKEN_KEYS.ACCESS_TOKEN) || localStorage.getItem(TOKEN_KEYS.TOKEN)),
    source: 'react',
    reason,
  });
};

// Safe localStorage wrapper
export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(TOKEN_KEYS.ACCESS_TOKEN) || localStorage.getItem(TOKEN_KEYS.TOKEN),
  setAccessToken: (token: string) => {
    localStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, token);
    localStorage.setItem(TOKEN_KEYS.TOKEN, token); // Next.js için
    emitAuthChange('token-updated');
  },
  removeAccessToken: () => {
    localStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(TOKEN_KEYS.TOKEN);
    emitAuthChange('token-cleared');
  },
  
  getRefreshToken: () => localStorage.getItem(TOKEN_KEYS.REFRESH_TOKEN),
  setRefreshToken: (token: string) => {
    localStorage.setItem(TOKEN_KEYS.REFRESH_TOKEN, token);
    emitAuthChange('refresh-token-updated');
  },
  removeRefreshToken: () => {
    localStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN);
    emitAuthChange('refresh-token-cleared');
  },
  
  // User bilgileri için yeni metodlar
  getUser: () => {
    const userData = localStorage.getItem(TOKEN_KEYS.USER);
    try {
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  },
  setUser: (user: any) => {
    localStorage.setItem(TOKEN_KEYS.USER, JSON.stringify(user));
    emitAuthChange('user-updated');
  },
  removeUser: () => {
    localStorage.removeItem(TOKEN_KEYS.USER);
    emitAuthChange('user-cleared');
  },
  
  clearAll: () => {
    localStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(TOKEN_KEYS.TOKEN);
    localStorage.removeItem(TOKEN_KEYS.USER);
    emitAuthChange('storage-cleared');
  }
};
