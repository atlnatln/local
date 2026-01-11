/**
 * Authentication utilities for Anka Platform
 * Handles server-side session management (httpOnly cookies)
 */

import { get, post } from './api-client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: {
    id: number;
    username: string;
    email: string;
  };
  message: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
}

/**
 * Login user with email and password
 * Session cookie is automatically set (httpOnly)
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  return post<LoginResponse>('/auth/login/', credentials);
}

/**
 * Logout user
 * Clears session cookie on server
 */
export async function logout(): Promise<void> {
  await post('/auth/logout/', {});
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  return get<User>('/auth/me/');
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  try {
    await getCurrentUser();
    return true;
  } catch {
    return false;
  }
}

/**
 * Refresh session (keep alive)
 */
export async function refreshSession(): Promise<void> {
  await post('/auth/refresh/', {});
}

/**
 * Change password
 */
export async function changePassword(
  oldPassword: string,
  newPassword: string
): Promise<{ message: string }> {
  return post('/auth/change-password/', {
    old_password: oldPassword,
    new_password: newPassword,
  });
}
