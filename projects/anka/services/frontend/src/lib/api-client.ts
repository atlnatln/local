/**
 * API client for Anka Platform
 *
 * Authentication is handled via HttpOnly cookies (set by the backend).
 * Every fetch uses `credentials: 'include'` so the browser automatically
 * attaches the JWT cookies — no manual Authorization header needed.
 *
 * On 401, the client transparently attempts a token refresh (once) before
 * falling back to a login redirect.
 */

const API_URL =
  typeof window !== 'undefined'
    ? window.location.origin
    : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function normalizeApiBase(rawUrl: string): string {
  const trimmed = rawUrl.replace(/\/+$/, '');

  // Allow callers to provide either a host (https://example.com) or an API root
  // (https://example.com/api). Also defensively collapse accidental double '/api'.
  if (/\/api(?:\/api)+$/.test(trimmed)) {
    return trimmed.replace(/(\/api)+$/, '/api');
  }

  return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
}

const API_BASE = normalizeApiBase(API_URL);

export interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
  skipAuth?: boolean;
  /** @internal — prevents infinite refresh loops */
  _isRetry?: boolean;
}

/** Mutex: prevent multiple concurrent refresh attempts */
let _refreshPromise: Promise<boolean> | null = null;

/**
 * Attempt to refresh the access token via the backend cookie-based flow.
 * Returns `true` if a new access token was obtained, `false` otherwise.
 */
async function tryRefreshToken(): Promise<boolean> {
  // De-duplicate: if a refresh is already in-flight, wait for it
  if (_refreshPromise) return _refreshPromise;

  _refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/refresh/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: '{}',
      });
      if (res.ok) {
        // Update the optimistic client-side flag
        if (typeof window !== 'undefined') {
          const expiresAt = new Date(Date.now() + 15 * 60 * 1000);
          localStorage.setItem('anka_authenticated', 'true');
          localStorage.setItem('anka_token_expires', expiresAt.toISOString());
        }
        return true;
      }
      return false;
    } catch {
      return false;
    } finally {
      _refreshPromise = null;
    }
  })();

  return _refreshPromise;
}

/**
 * Handle terminal 401 — clear auth flag and redirect to login.
 * Preserves the current page path so the user returns here after re-login.
 */
async function handle401(): Promise<void> {
  if (typeof window !== 'undefined') {
    // Clear optimistic client-side flag
    localStorage.removeItem('anka_authenticated');
    localStorage.removeItem('anka_token_expires');
    // Clean up any legacy keys
    localStorage.removeItem('anka_access_token');
    localStorage.removeItem('anka_refresh_token');
    // Preserve current path (+query) for redirect-after-login
    const currentPath = `${window.location.pathname}${window.location.search || ''}`;
    const redirectParam =
      currentPath && currentPath !== '/' && currentPath !== '/login'
        ? `?redirect=${encodeURIComponent(currentPath)}`
        : '';
    window.location.href = `/login${redirectParam}`;
  }
}

/**
 * Fetch wrapper with cookie-based JWT, automatic token refresh, and error handling.
 * The browser sends HttpOnly cookies automatically via credentials: 'include'.
 *
 * On a 401 response the client will:
 *  1. Attempt a silent token refresh (POST /api/auth/refresh/)
 *  2. If refresh succeeds → retry the original request once
 *  3. If refresh fails → redirect to /login
 */
export async function fetchAPI<T = any>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { skipAuth = false, _isRetry = false, ...fetchOptions } = options;
  const url = `${API_BASE}${endpoint}`;
  
  const mergedHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...fetchOptions.headers,
  };

  const defaultOptions: FetchOptions = {
    ...fetchOptions,
    credentials: 'include',          // ← send HttpOnly cookies
    headers: mergedHeaders,
  };

  const response = await fetch(url, defaultOptions);

  // Handle 401 — try silent token refresh, then retry once
  if (response.status === 401 && !_isRetry && !skipAuth) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      // Retry the original request with _isRetry flag to avoid infinite loop
      return fetchAPI<T>(endpoint, { ...options, _isRetry: true });
    }
    // Refresh failed → hard redirect to login
    await handle401();
    throw new Error('Unauthorized');
  }

  if (response.status === 401) {
    await handle401();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    // Build a human-readable error from DRF response formats:
    // - { detail: "..." }
    // - { error: "..." }
    // - { field_name: ["error1", ...] }  (field-level validation)
    const message =
      errorData.detail ||
      errorData.error ||
      errorData.message ||
      // Collect first field-level error
      Object.values(errorData)
        .flat()
        .find((v): v is string => typeof v === 'string') ||
      `API Error: ${response.statusText}`;
    throw new Error(message);
  }

  if (response.status === 204) {
    return {} as T; // No content
  }

  return response.json();
}

/**
 * GET request
 */
export async function get<T = any>(
  endpoint: string,
  skipAuth: boolean = false
): Promise<T> {
  return fetchAPI<T>(endpoint, { method: 'GET', skipAuth });
}

/**
 * POST request
 */
export async function post<T = any>(
  endpoint: string,
  data: any,
  skipAuth: boolean = false
): Promise<T> {
  return fetchAPI<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
    skipAuth,
  });
}

/**
 * PUT request
 */
export async function put<T = any>(
  endpoint: string,
  data: any,
  skipAuth: boolean = false
): Promise<T> {
  return fetchAPI<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
    skipAuth,
  });
}

/**
 * PATCH request
 */
export async function patch<T = any>(
  endpoint: string,
  data: any,
  skipAuth: boolean = false
): Promise<T> {
  return fetchAPI<T>(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data),
    skipAuth,
  });
}

/**
 * DELETE request
 */
export async function del<T = any>(
  endpoint: string,
  skipAuth: boolean = false
): Promise<T> {
  return fetchAPI<T>(endpoint, { method: 'DELETE', skipAuth });
}
