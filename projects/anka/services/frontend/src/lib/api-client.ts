/**
 * API client for Anka Platform
 * Handles JWT authentication, requests, and error handling
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api`;

export interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
  skipAuth?: boolean;
}

/**
 * Get Authorization header with JWT token
 */
function getAuthorizationHeader(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  
  const token = localStorage.getItem('anka_access_token');
  if (!token) return {};
  
  return {
    'Authorization': `Bearer ${token}`,
  };
}

/**
 * Handle 401 responses - refresh token or redirect to login
 */
async function handle401(): Promise<void> {
  // Clear tokens and redirect to login
  if (typeof window !== 'undefined') {
    localStorage.removeItem('anka_access_token');
    localStorage.removeItem('anka_refresh_token');
    localStorage.removeItem('anka_token_expires');
    window.location.href = '/login';
  }
}

/**
 * Fetch wrapper with JWT token and error handling
 */
export async function fetchAPI<T = any>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { skipAuth = false, ...fetchOptions } = options;
  const url = `${API_BASE}${endpoint}`;
  
  const defaultOptions: FetchOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(!skipAuth && getAuthorizationHeader()),
      ...fetchOptions.headers,
    },
    ...fetchOptions,
  };

  const response = await fetch(url, defaultOptions);

  // Handle 401 - redirect to login
  if (response.status === 401) {
    await handle401();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.error || `API Error: ${response.statusText}`);
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
