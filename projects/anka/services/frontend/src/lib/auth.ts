/**
 * JWT Authentication utilities for Anka Platform
 *
 * Tokens are stored in HttpOnly cookies set by the backend.
 * The frontend CANNOT read them (by design – XSS protection).
 *
 * This module keeps:
 *   - A lightweight "is-logged-in" flag in localStorage so the
 *     client can do optimistic UI checks without an API call.
 *   - Token-expiry tracking for proactive refresh.
 *
 * Migration note (ADR-0007): Prior to this change tokens were in
 * localStorage + non-HttpOnly cookies. The backend now sets
 * HttpOnly / Secure / SameSite=Lax cookies on every auth response.
 */

import { get, post } from './api-client';

// Lightweight client-side flag (NOT the actual token)
const AUTH_FLAG_KEY = 'anka_authenticated';
const TOKEN_EXPIRES_KEY = 'anka_token_expires';

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface LoginResponse extends TokenPair {
  user: User;
}

export interface GoogleLoginRequest {
  id_token: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile?: {
    avatar_url: string;
    phone: string;
    language: string;
    timezone: string;
  };
  organizations?: Array<{
    id: string;
    name: string;
    role: string;
    slug: string;
  }>;
  date_joined: string;
}

// ─── helpers ──────────────────────────────────────────────

/** Mark the browser as "logged in" (optimistic flag only). */
function setAuthFlag(): void {
  if (typeof window === 'undefined') return;
  const expiresAt = new Date(Date.now() + 15 * 60 * 1000); // 15 min
  localStorage.setItem(AUTH_FLAG_KEY, 'true');
  localStorage.setItem(TOKEN_EXPIRES_KEY, expiresAt.toISOString());
}

/** Clear the optimistic flag. */
function clearAuthFlag(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(AUTH_FLAG_KEY);
  localStorage.removeItem(TOKEN_EXPIRES_KEY);

  // Clean up legacy keys from pre-cookie migration
  localStorage.removeItem('anka_access_token');
  localStorage.removeItem('anka_refresh_token');
}

// ─── public API ───────────────────────────────────────────

/**
 * Save authentication state after a successful login/refresh.
 * Actual JWT tokens are in HttpOnly cookies (set by the backend).
 */
export function saveTokens(_tokens: TokenPair): void {
  setAuthFlag();
}

/**
 * Check if the user *appears* to be authenticated.
 * This is optimistic – the server is the source of truth.
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(AUTH_FLAG_KEY) === 'true' && !isTokenExpired();
}

/** Access token is now HttpOnly – not readable in JS. */
export function getAccessToken(): string | null {
  // Kept for interface compat; always returns null.
  return null;
}

/** Refresh token is now HttpOnly – not readable in JS. */
export function getRefreshToken(): string | null {
  return null;
}

export function isTokenExpired(): boolean {
  if (typeof window === 'undefined') return true;
  const exp = localStorage.getItem(TOKEN_EXPIRES_KEY);
  if (!exp) return true;
  return new Date() > new Date(exp);
}

export function clearTokens(): void {
  clearAuthFlag();
}

// ─── auth flows ───────────────────────────────────────────

/**
 * Login user with Google ID token (Google-only MVP).
 * Backend sets HttpOnly cookies in the response.
 */
export async function loginWithGoogleIdToken(idToken: string): Promise<LoginResponse> {
  const response = await post<LoginResponse>(
    '/auth/google/',
    { id_token: idToken } satisfies GoogleLoginRequest,
  );
  setAuthFlag();
  return response;
}

/**
 * Refresh the access token.
 * The refresh token is sent automatically via the HttpOnly cookie.
 */
export async function refreshAccessToken(): Promise<string> {
  // Body is empty – backend reads refresh from cookie
  const response = await post<{ access: string }>('/auth/refresh/', {});
  setAuthFlag();
  return response.access;
}

/**
 * Logout – tells backend to blacklist the refresh token.
 * Backend also clears HttpOnly cookies.
 */
export async function logout(): Promise<void> {
  try {
    // Body is empty – backend reads refresh from cookie
    await post('/auth/logout/', {});
  } catch {
    // Ignore errors (token might already be expired)
  }
  clearAuthFlag();
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  return get<User>('/auth/me/');
}

/**
 * Change password
 */
export async function changePassword(
  oldPassword: string,
  newPassword: string,
  newPassword2: string,
): Promise<{ detail: string }> {
  return post('/auth/change-password/', {
    old_password: oldPassword,
    new_password: newPassword,
    new_password2: newPassword2,
  });
}

