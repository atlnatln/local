export const AUTH_CHANGE_EVENT = 'webimar:auth-changed';

export const AUTH_STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  TOKEN: 'token',
  LEGACY_ACCESS_TOKEN: 'accessToken',
  LEGACY_REFRESH_TOKEN: 'refreshToken',
  USER: 'user',
  SHARED_STATE: 'webimar_auth_state',
} as const;

export type AuthEventSource = 'react' | 'nextjs' | 'backend';

export interface SharedAuthState<TUser = any> {
  isAuthenticated: boolean;
  user: TUser | null;
  timestamp: number;
  source: AuthEventSource;
  reason?: string;
}

export interface AuthChangeDetail {
  isAuthenticated: boolean;
  source: AuthEventSource;
  reason?: string;
}

const canUseDOM = () => typeof window !== 'undefined';

const safeStorage = {
  getItem(key: string): string | null {
    if (!canUseDOM()) return null;
    try {
      return window.localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  setItem(key: string, value: string) {
    if (!canUseDOM()) return;
    try {
      window.localStorage.setItem(key, value);
    } catch {
      // ignore storage quota / privacy mode failures
    }
  },
  removeItem(key: string) {
    if (!canUseDOM()) return;
    try {
      window.localStorage.removeItem(key);
    } catch {
      // ignore storage quota / privacy mode failures
    }
  },
};

export const dispatchAuthChange = (detail: AuthChangeDetail) => {
  if (!canUseDOM()) return;
  window.dispatchEvent(new CustomEvent<AuthChangeDetail>(AUTH_CHANGE_EVENT, { detail }));
};

export const readStoredUser = <TUser = any>(): TUser | null => {
  const raw = safeStorage.getItem(AUTH_STORAGE_KEYS.USER);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as TUser;
  } catch {
    return null;
  }
};

export const readSharedAuthState = <TUser = any>(): SharedAuthState<TUser> | null => {
  const raw = safeStorage.getItem(AUTH_STORAGE_KEYS.SHARED_STATE);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as SharedAuthState<TUser>;
  } catch {
    return null;
  }
};

export const writeSharedAuthState = <TUser = any>(params: {
  isAuthenticated: boolean;
  user: TUser | null;
  source: AuthEventSource;
  reason?: string;
}) => {
  const nextState: SharedAuthState<TUser> = {
    isAuthenticated: params.isAuthenticated,
    user: params.user,
    source: params.source,
    reason: params.reason,
    timestamp: Date.now(),
  };

  safeStorage.setItem(AUTH_STORAGE_KEYS.SHARED_STATE, JSON.stringify(nextState));
  dispatchAuthChange({
    isAuthenticated: nextState.isAuthenticated,
    source: nextState.source,
    reason: nextState.reason,
  });

  return nextState;
};

export const persistAuthSession = <TUser = any>(params: {
  accessToken: string;
  refreshToken?: string | null;
  user: TUser;
  source?: AuthEventSource;
  reason?: string;
}) => {
  safeStorage.setItem(AUTH_STORAGE_KEYS.ACCESS_TOKEN, params.accessToken);
  safeStorage.setItem(AUTH_STORAGE_KEYS.TOKEN, params.accessToken);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.LEGACY_ACCESS_TOKEN);

  if (params.refreshToken) {
    safeStorage.setItem(AUTH_STORAGE_KEYS.REFRESH_TOKEN, params.refreshToken);
    safeStorage.removeItem(AUTH_STORAGE_KEYS.LEGACY_REFRESH_TOKEN);
  }

  safeStorage.setItem(AUTH_STORAGE_KEYS.USER, JSON.stringify(params.user));

  return writeSharedAuthState({
    isAuthenticated: true,
    user: params.user,
    source: params.source || 'react',
    reason: params.reason,
  });
};

export const clearAuthSessionStorage = (params?: {
  source?: AuthEventSource;
  reason?: string;
}) => {
  safeStorage.removeItem(AUTH_STORAGE_KEYS.ACCESS_TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.REFRESH_TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.LEGACY_ACCESS_TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.LEGACY_REFRESH_TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.USER);
  safeStorage.removeItem('returnUrl');

  if (typeof window !== 'undefined') {
    try {
      window.sessionStorage.removeItem('returnUrl');
    } catch {
      // ignore browser storage restrictions
    }
  }

  return writeSharedAuthState({
    isAuthenticated: false,
    user: null,
    source: params?.source || 'react',
    reason: params?.reason,
  });
};
