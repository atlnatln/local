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

export interface AuthUser {
  id?: number;
  email?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  [key: string]: unknown;
}

export interface SharedAuthState<TUser = AuthUser> {
  isAuthenticated: boolean;
  user: TUser | null;
  timestamp: number;
  source: AuthEventSource;
  reason?: string;
}

interface FetchUserResult {
  ok: boolean;
  status: number;
  user: AuthUser | null;
  networkError?: boolean;
}

interface RefreshResult {
  ok: boolean;
  status: number;
  accessToken: string | null;
  refreshToken: string | null;
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
      // ignore
    }
  },
  removeItem(key: string) {
    if (!canUseDOM()) return;
    try {
      window.localStorage.removeItem(key);
    } catch {
      // ignore
    }
  },
};

const getCookieDomain = (): string | null => {
  if (!canUseDOM()) return null;

  const host = window.location.hostname;
  if (host.endsWith('tarimimar.com.tr')) {
    return '.tarimimar.com.tr';
  }

  return null;
};

export const clearAuthCookies = () => {
  if (!canUseDOM()) return;

  const expires = 'Thu, 01 Jan 1970 00:00:00 GMT';
  const attrs = [`path=/`, `expires=${expires}`];
  const domain = getCookieDomain();
  if (domain) {
    attrs.push(`Domain=${domain}`);
  }

  document.cookie = [`webimar_auth=`, ...attrs].join('; ');
  document.cookie = [`webimar_user=`, ...attrs].join('; ');
};

export const dispatchAuthChange = (detail: {
  isAuthenticated: boolean;
  source: AuthEventSource;
  reason?: string;
}) => {
  if (!canUseDOM()) return;
  window.dispatchEvent(new CustomEvent(AUTH_CHANGE_EVENT, { detail }));
};

export const readStoredUser = <TUser = AuthUser>(): TUser | null => {
  const raw = safeStorage.getItem(AUTH_STORAGE_KEYS.USER);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as TUser;
  } catch {
    return null;
  }
};

export const readSharedAuthState = <TUser = AuthUser>(): SharedAuthState<TUser> | null => {
  const raw = safeStorage.getItem(AUTH_STORAGE_KEYS.SHARED_STATE);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as SharedAuthState<TUser>;
  } catch {
    return null;
  }
};

export const readStoredTokens = () => ({
  accessToken: safeStorage.getItem(AUTH_STORAGE_KEYS.ACCESS_TOKEN) || safeStorage.getItem(AUTH_STORAGE_KEYS.TOKEN),
  refreshToken: safeStorage.getItem(AUTH_STORAGE_KEYS.REFRESH_TOKEN),
});

export const writeSharedAuthState = (params: {
  isAuthenticated: boolean;
  user: AuthUser | null;
  reason?: string;
  source?: AuthEventSource;
}) => {
  const nextState: SharedAuthState = {
    isAuthenticated: params.isAuthenticated,
    user: params.user,
    reason: params.reason,
    source: params.source || 'nextjs',
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

export const persistAuthSession = (params: {
  accessToken: string;
  refreshToken?: string | null;
  user: AuthUser;
  reason?: string;
  source?: AuthEventSource;
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
    reason: params.reason,
    source: params.source || 'nextjs',
  });
};

export const clearAuthSession = (params?: {
  reason?: string;
  source?: AuthEventSource;
}) => {
  safeStorage.removeItem(AUTH_STORAGE_KEYS.ACCESS_TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.REFRESH_TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.LEGACY_ACCESS_TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.LEGACY_REFRESH_TOKEN);
  safeStorage.removeItem(AUTH_STORAGE_KEYS.USER);
  safeStorage.removeItem('returnUrl');

  if (canUseDOM()) {
    try {
      window.sessionStorage.removeItem('returnUrl');
    } catch {
      // ignore private mode / browser restrictions
    }
  }

  clearAuthCookies();

  return writeSharedAuthState({
    isAuthenticated: false,
    user: null,
    reason: params?.reason,
    source: params?.source || 'nextjs',
  });
};

export const getApiBaseUrl = () => {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (configured) {
    return configured.replace(/\/$/, '');
  }

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (backendUrl) {
    return `${backendUrl.replace(/\/$/, '')}/api`;
  }

  if (canUseDOM()) {
    return `${window.location.origin.replace(/\/$/, '')}/api`;
  }

  return 'https://tarimimar.com.tr/api';
};

export const fetchCurrentUser = async (accessToken: string): Promise<FetchUserResult> => {
  try {
    const response = await fetch(`${getApiBaseUrl()}/accounts/me/`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        user: null,
      };
    }

    const user = (await response.json()) as AuthUser;
    return {
      ok: true,
      status: response.status,
      user,
    };
  } catch {
    return {
      ok: false,
      status: 0,
      user: null,
      networkError: true,
    };
  }
};

export const refreshAccessToken = async (refreshToken: string): Promise<RefreshResult> => {
  try {
    const response = await fetch(`${getApiBaseUrl()}/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        accessToken: null,
        refreshToken: null,
      };
    }

    const data = await response.json();
    return {
      ok: true,
      status: response.status,
      accessToken: data.access || null,
      refreshToken: data.refresh || refreshToken,
    };
  } catch {
    return {
      ok: false,
      status: 0,
      accessToken: null,
      refreshToken: null,
    };
  }
};

export const resolveAuthenticatedSession = async (): Promise<{
  isAuthenticated: boolean;
  user: AuthUser | null;
  accessToken: string | null;
  refreshToken: string | null;
}> => {
  const sharedState = readSharedAuthState();
  const storedUser = readStoredUser<AuthUser>() || sharedState?.user || null;
  let { accessToken, refreshToken } = readStoredTokens();

  if (!accessToken && !refreshToken) {
    return {
      isAuthenticated: false,
      user: null,
      accessToken: null,
      refreshToken: null,
    };
  }

  if (!accessToken && refreshToken) {
    const refreshed = await refreshAccessToken(refreshToken);
    if (!refreshed.ok || !refreshed.accessToken) {
      clearAuthSession({ reason: 'refresh-failed' });
      return {
        isAuthenticated: false,
        user: null,
        accessToken: null,
        refreshToken: null,
      };
    }

    accessToken = refreshed.accessToken;
    refreshToken = refreshed.refreshToken || refreshToken;
  }

  if (!accessToken) {
    clearAuthSession({ reason: 'missing-access-token' });
    return {
      isAuthenticated: false,
      user: null,
      accessToken: null,
      refreshToken: null,
    };
  }

  let meResult = await fetchCurrentUser(accessToken);

  if (!meResult.ok && meResult.status === 401 && refreshToken) {
    const refreshed = await refreshAccessToken(refreshToken);
    if (!refreshed.ok || !refreshed.accessToken) {
      clearAuthSession({ reason: 'refresh-failed' });
      return {
        isAuthenticated: false,
        user: null,
        accessToken: null,
        refreshToken: null,
      };
    }

    accessToken = refreshed.accessToken;
    refreshToken = refreshed.refreshToken || refreshToken;
    meResult = await fetchCurrentUser(accessToken);
  }

  if (meResult.ok && meResult.user) {
    persistAuthSession({
      accessToken,
      refreshToken,
      user: meResult.user,
      reason: 'verified-session',
    });

    return {
      isAuthenticated: true,
      user: meResult.user,
      accessToken,
      refreshToken,
    };
  }

  if (meResult.networkError && storedUser) {
    return {
      isAuthenticated: true,
      user: storedUser,
      accessToken,
      refreshToken,
    };
  }

  clearAuthSession({ reason: meResult.status === 401 ? 'session-expired' : 'session-invalid' });
  return {
    isAuthenticated: false,
    user: null,
    accessToken: null,
    refreshToken: null,
  };
};

export const logoutFromBackend = async () => {
  const { accessToken, refreshToken } = readStoredTokens();
  if (!accessToken) return;

  const controller = typeof AbortController !== 'undefined'
    ? new AbortController()
    : null;
  const timeoutId = controller
    ? window.setTimeout(() => controller.abort(), 5000)
    : null;

  try {
    await fetch(`${getApiBaseUrl()}/accounts/me/logout/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
      keepalive: true,
      signal: controller?.signal,
    });
  } catch {
    // best effort only
  } finally {
    if (timeoutId !== null) {
      window.clearTimeout(timeoutId);
    }
  }
};
