/**
 * JWT Authentication utilities for Anka Platform
 * Handles JWT token management with localStorage
 */

import { get, post } from './api-client';

// Token storage keys
const ACCESS_TOKEN_KEY = 'anka_access_token';
const REFRESH_TOKEN_KEY = 'anka_refresh_token';
const TOKEN_EXPIRES_KEY = 'anka_token_expires';

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse extends TokenPair {
  user: User;
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

/**
 * Save JWT tokens to localStorage
 */
export function saveTokens(tokens: TokenPair): void {
  const now = new Date();
  const expiresAt = new Date(now.getTime() + 15 * 60 * 1000); // 15 minutes

  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
  localStorage.setItem(TOKEN_EXPIRES_KEY, expiresAt.toISOString());
}

/**
 * Get access token from localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Get refresh token from localStorage
 */
export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Check if token is expired
 */
export function isTokenExpired(): boolean {
  if (typeof window === 'undefined') return true;
  
  const expiresAt = localStorage.getItem(TOKEN_EXPIRES_KEY);
  if (!expiresAt) return true;
  
  return new Date() > new Date(expiresAt);
}

/**
 * Clear all tokens
 */
export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRES_KEY);
}

/**
 * Login user with username and password
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await post<LoginResponse>('/auth/login/', credentials);
  saveTokens({
    access: response.access,
    refresh: response.refresh,
  });
  return response;
}

/**
 * Refresh access token using refresh token
 */
export async function refreshAccessToken(): Promise<string> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) throw new Error('No refresh token available');

  const response = await post<{ access: string }>('/auth/refresh/', {
    refresh: refreshToken,
  });

  const now = new Date();
  const expiresAt = new Date(now.getTime() + 15 * 60 * 1000);

  localStorage.setItem(ACCESS_TOKEN_KEY, response.access);
  localStorage.setItem(TOKEN_EXPIRES_KEY, expiresAt.toISOString());

  return response.access;
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
  try {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      await post('/auth/logout/', { refresh: refreshToken });
    }
  } catch (error) {
    // Silently fail - clear tokens anyway
    console.error('Logout request failed:', error);
  } finally {
    clearTokens();
  }
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  return get<User>('/auth/me/');
}

/**
 * Check if user is authenticated (has valid token)
 */
export function isAuthenticated(): boolean {
  const token = getAccessToken();
  return !!token && !isTokenExpired();
}

/**
 * Register new user
 */
export async function register(userData: {
  username: string;
  email: string;
  password: string;
  password2?: string;
  first_name?: string;
  last_name?: string;
}): Promise<User> {
  // Ensure password2 is set (API expects both password and password2)
  const registerData = {
    ...userData,
    password2: userData.password2 || userData.password,
  };
  return post<User>('/auth/register/', registerData);
}

/**
 * Change password
 */
export async function changePassword(
  oldPassword: string,
  newPassword: string,
  newPassword2: string
): Promise<{ detail: string }> {
  return post('/auth/change-password/', {
    old_password: oldPassword,
    new_password: newPassword,
    new_password2: newPassword2,
  });
}

