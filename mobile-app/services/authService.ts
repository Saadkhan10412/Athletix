/**
 * ATHLETIX — Authentication Service
 * mobile-app/services/authService.ts
 *
 * Provides authentication and session management functions for the mobile application.
 *
 * Core Capabilities:
 * - User Signup & Login: Communicates with backend endpoints (/auth/signup, /auth/login) to obtain JWT tokens.
 * - Session Persistence: Stores user profile and access token locally in AsyncStorage and syncs with Supabase.
 * - Session Restoration: Rehydrates the active user session on application startup or deep-linking.
 * - Password Management: Dispatches password reset emails with dynamic redirection URLs and submits new credentials.
 * - Secure Logout: Cleans up push notification device tokens and deletes locally cached session data.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import api from './api';
import { supabase } from './supabase';
export { supabase };

export type UserRole =
  | 'athlete'
  | 'official'
  | 'admin';

export interface SignupPayload {
  name: string;
  email: string;
  password: string;
  role: UserRole;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthUser {
  userId: string;
  email: string;
  name: string;
  role: UserRole;
  accessToken: string;
}

const TOKEN_KEY = 'athletix_access_token';
const USER_KEY = 'athletix_user';

// ─── Signup Function ──────────────────────────────────────────────────────────

/**
 * Registers a new user with the specified role (athlete, official, admin).
 * Persists session credentials upon successful registration.
 */
export async function signup(
  payload: SignupPayload
): Promise<AuthUser> {
  const response = await api.post(
    '/auth/signup',
    payload
  );

  const { data } = response.data;

  const authUser: AuthUser = {
    userId: data.user_id,
    email: data.email,
    name: data.name,
    role: data.role,
    accessToken: data.access_token,
  };

  await persistSession(authUser);
  return authUser;
}

// ─── Login Function ───────────────────────────────────────────────────────────

/**
 * Authenticates user credentials against the backend API and stores the returned JWT.
 */
export async function login(
  payload: LoginPayload
): Promise<AuthUser> {
  const response = await api.post(
    '/auth/login',
    payload
  );

  const { data } = response.data;

  const authUser: AuthUser = {
    userId: data.user_id,
    email: data.email,
    name: data.name,
    role: data.role,
    accessToken: data.access_token,
  };

  await persistSession(authUser);
  return authUser;
}

// ─── Logout Function ──────────────────────────────────────────────────────────

/**
 * Terminates user session, notifies backend, unregisters push tokens, and purges local storage.
 */
export async function logout(): Promise<void> {
  try {
    await api.post('/auth/logout');
  } catch {
    // Continue with client-side cleanup even if network request fails
  }

  try {
    const { unregisterPushToken } = require('./notificationService');
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    if (token) {
      await unregisterPushToken(token);
    }
  } catch {
    // Non-critical push token cleanup failure
  }

  await AsyncStorage.multiRemove([
    TOKEN_KEY,
    USER_KEY,
  ]);
}

// ─── Restore Session Function ─────────────────────────────────────────────────

/**
 * Restores cached user session from AsyncStorage on app launch.
 * Refreshes Supabase authentication tokens if needed.
 */
export async function restoreSession(): Promise<AuthUser | null> {
  try {
    let currentToken: string | null = null;
    try {
      const { data: sessionData } = await supabase.auth.getSession();
      currentToken = sessionData?.session?.access_token ?? null;

      if (!currentToken) {
        const { data: refreshData } = await supabase.auth.refreshSession();
        currentToken = refreshData?.session?.access_token ?? null;
      }
    } catch {
      // Fall back to local AsyncStorage token
    }

    const rawUser = await AsyncStorage.getItem(USER_KEY);
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    const activeToken = currentToken || token;

    if (!rawUser || !activeToken) {
      return null;
    }

    if (currentToken && currentToken !== token) {
      await AsyncStorage.setItem(TOKEN_KEY, currentToken);
    }

    const storedUser = JSON.parse(rawUser) as AuthUser;

    return {
      ...storedUser,
      accessToken: activeToken,
    };
  } catch {
    await AsyncStorage.multiRemove([
      TOKEN_KEY,
      USER_KEY,
    ]);
    return null;
  }
}

// ─── Forgot Password Function ─────────────────────────────────────────────────

/**
 * Requests a password reset link for the provided email address.
 * Resolves redirect URL dynamically based on the current window origin.
 */
export async function forgotPassword(
  email: string
): Promise<string> {
  const cleanEmail = email.trim().toLowerCase();
  
  // Resolve password reset redirect URL dynamically
  const redirectUrl =
    typeof window !== 'undefined' && window.location?.origin
      ? `${window.location.origin}/reset-password`
      : 'http://localhost:8081/reset-password';

  // 1. Primary: Direct Supabase Auth reset dispatch
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(cleanEmail, {
      redirectTo: redirectUrl,
    });
    if (!error) {
      return 'Password reset link has been dispatched to your email address.';
    }
  } catch {
    // Fall back to backend reset dispatch
  }

  // 2. Secondary: Backend API dispatch fallback
  try {
    await api.post('/auth/forgot-password', { email: cleanEmail });
  } catch {
    // Suppress API errors to protect user privacy
  }

  return 'Password reset link has been dispatched to your email address.';
}

// ─── Reset Password Function ──────────────────────────────────────────────────

/**
 * Updates user password given a valid reset access token.
 */
export async function resetPassword(
  accessToken: string,
  newPassword: string
): Promise<string> {
  const response = await api.post(
    '/auth/reset-password',
    {
      access_token: accessToken,
      new_password: newPassword,
    }
  );

  return (
    response.data?.data?.message ??
    'Password updated successfully.'
  );
}

// ─── Internal Storage Helpers ─────────────────────────────────────────────────

export async function getAuthToken(): Promise<string | null> {
  return AsyncStorage.getItem(TOKEN_KEY);
}

async function persistSession(user: AuthUser): Promise<void> {
  await AsyncStorage.multiSet([
    [TOKEN_KEY, user.accessToken],
    [USER_KEY, JSON.stringify(user)],
  ]);
}