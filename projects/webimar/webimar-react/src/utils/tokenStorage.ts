// Token management constants - Next.js ile uyumlu key'ler
export const TOKEN_KEYS = {
  ACCESS_TOKEN: 'access_token', // Next.js uyumlu
  REFRESH_TOKEN: 'refresh_token',
  TOKEN: 'token', // Next.js için alternatif key
  USER: 'user' // User bilgileri için
} as const;

// Safe localStorage wrapper
export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(TOKEN_KEYS.ACCESS_TOKEN) || localStorage.getItem(TOKEN_KEYS.TOKEN),
  setAccessToken: (token: string) => {
    localStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, token);
    localStorage.setItem(TOKEN_KEYS.TOKEN, token); // Next.js için
    // Next.js Layout'a haber ver
    window.dispatchEvent(new Event('storage'));
  },
  removeAccessToken: () => {
    localStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(TOKEN_KEYS.TOKEN);
    window.dispatchEvent(new Event('storage'));
  },
  
  getRefreshToken: () => localStorage.getItem(TOKEN_KEYS.REFRESH_TOKEN),
  setRefreshToken: (token: string) => {
    localStorage.setItem(TOKEN_KEYS.REFRESH_TOKEN, token);
    window.dispatchEvent(new Event('storage'));
  },
  removeRefreshToken: () => {
    localStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN);
    window.dispatchEvent(new Event('storage'));
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
    window.dispatchEvent(new Event('storage'));
  },
  removeUser: () => {
    localStorage.removeItem(TOKEN_KEYS.USER);
    window.dispatchEvent(new Event('storage'));
  },
  
  clearAll: () => {
    localStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(TOKEN_KEYS.TOKEN);
    localStorage.removeItem(TOKEN_KEYS.USER);
    window.dispatchEvent(new Event('storage'));
  }
};
