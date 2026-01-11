/**
 * API client for Anka Platform
 * Handles authentication, requests, and error handling
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api`;

export interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
}

/**
 * Fetch wrapper with automatic cookie inclusion and error handling
 */
export async function fetchAPI<T = any>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  
  const defaultOptions: FetchOptions = {
    credentials: 'include', // Include cookies for session auth
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, defaultOptions);

  // Handle 401 - redirect to login
  if (response.status === 401) {
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.statusText}`);
  }

  if (response.status === 204) {
    return {} as T; // No content
  }

  return response.json();
}

/**
 * GET request
 */
export async function get<T = any>(endpoint: string): Promise<T> {
  return fetchAPI<T>(endpoint, { method: 'GET' });
}

/**
 * POST request
 */
export async function post<T = any>(
  endpoint: string,
  data: any
): Promise<T> {
  return fetchAPI<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * PUT request
 */
export async function put<T = any>(
  endpoint: string,
  data: any
): Promise<T> {
  return fetchAPI<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * PATCH request
 */
export async function patch<T = any>(
  endpoint: string,
  data: any
): Promise<T> {
  return fetchAPI<T>(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * DELETE request
 */
export async function del<T = any>(endpoint: string): Promise<T> {
  return fetchAPI<T>(endpoint, { method: 'DELETE' });
}
