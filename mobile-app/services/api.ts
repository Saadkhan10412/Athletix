/**
 * ATHLETIX — API HTTP Client (Axios Instance)
 * mobile-app/services/api.ts
 *
 * This module exports a configured Axios instance used by all frontend services
 * to communicate with the FastAPI backend.
 *
 * Key Functionalities:
 * - Dynamic Base URL resolution (prioritizing EXPO_PUBLIC_API_BASE_URL).
 * - Automatic Request Interception: Injects stored JWT Bearer token into Authorization headers.
 * - Response Interception & Error Normalization: Converts varied HTTP errors (network, timeout,
 *   401 Unauthorized, 403 Forbidden, 500 Internal Server Error) into standardized, user-friendly messages.
 * - Automatic Session Cleanup: Flushes local authentication credentials when receiving 401s on protected endpoints.
 */

import axios, {
  type AxiosError,
  type AxiosInstance,
} from 'axios';

import AsyncStorage from '@react-native-async-storage/async-storage';
import { supabase } from './supabase';

// ─── Configuration & URL Resolution ──────────────────────────────────────────

// Fallback development API URL if not explicitly defined in environment
const DEFAULT_API_URL = 'http://localhost:8000/api/v1';

/**
 * Resolves the active backend API base URL.
 * 1. Checks EXPO_PUBLIC_API_BASE_URL environment variable.
 * 2. If running in web mode on localhost, routes to standard local backend port 8000.
 * 3. Falls back to default backend URL.
 */
function resolveBaseUrl(): string {
  const configured = process.env.EXPO_PUBLIC_API_BASE_URL?.trim();
  if (configured) {
    return configured.replace(/\/+$/, '');
  }

  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const host = window.location.hostname;
    if (host === 'localhost' || host === '127.0.0.1') {
      return `http://${host}:8000/api/v1`;
    }
  }

  return DEFAULT_API_URL;
}

const BASE_URL = resolveBaseUrl();

// Storage key used across the application for persisting authentication tokens
const TOKEN_KEY = 'athletix_access_token';

// ─── Error Response Types ────────────────────────────────────────────────────

/**
 * Standard error response structure returned by the FastAPI backend.
 */
interface BackendErrorPayload {
  error?: {
    code?: string;
    message?: string;
  };

  detail?:
  | string
  | {
    error?: {
      code?: string;
      message?: string;
    };
    message?: string;
  };

  message?: string;
}

// ─── Axios Instance ──────────────────────────────────────────────────────────

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  // 120-second timeout allows sufficient time for video uploads and AI inference processing
  timeout: 120_000,
});

// ─── Request Interceptor: Inject JWT Bearer Token ─────────────────────────────

api.interceptors.request.use(
  async (config) => {
    let token = await AsyncStorage.getItem(TOKEN_KEY);

    // If local token not found, check active Supabase Auth session as fallback
    if (!token) {
      try {
        const { data } = await supabase.auth.getSession();
        if (data?.session?.access_token) {
          token = data.session.access_token;
          await AsyncStorage.setItem(TOKEN_KEY, token);
        }
      } catch {
        // Fallback silently if session fetch fails
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error: unknown) => Promise.reject(error)
);

// ─── Response Interceptor: Normalize Errors ──────────────────────────────────

api.interceptors.response.use(
  (response) => response,

  (error: AxiosError<BackendErrorPayload>) => {
    const serverData = error.response?.data;
    const detail = serverData?.detail;

    // Extract message from standard backend payload patterns
    const serverMessage =
      serverData?.error?.message ??
      (typeof detail === 'object'
        ? detail?.error?.message ?? detail?.message
        : undefined) ??
      (typeof detail === 'string'
        ? detail
        : undefined) ??
      serverData?.message;

    let userMessage: string;

    if (serverMessage) {
      userMessage = serverMessage;
    } else if (
      error.code === 'ECONNABORTED' ||
      error.code === 'ETIMEDOUT'
    ) {
      userMessage = 'Request timed out. Please check your connection and try again.';
    } else if (
      error.code === 'ERR_NETWORK' ||
      !error.response
    ) {
      userMessage = 'Unable to connect to the server. Please verify backend service availability.';
    } else if (error.response.status >= 500) {
      userMessage = 'Server error occurred. Please try again after some time.';
    } else if (error.response.status === 401) {
      userMessage = 'Invalid credentials or your session has expired.';

      // Token expiration on protected route -> automatically trigger store cleanup
      const isAuthRoute = error.config?.url?.includes('/auth/');
      if (!isAuthRoute) {
        void AsyncStorage.multiRemove([TOKEN_KEY, 'athletix_user']).then(() => {
          try {
            const { useAuthStore } = require('../stores/useAuthStore');
            useAuthStore.getState().setUser(null);
          } catch {
            // Ignore if store is not yet mounted
          }
        });
      }
    } else if (error.response.status === 403) {
      userMessage = 'You are not authorized to perform this action.';
    } else if (error.response.status === 404) {
      userMessage = 'The requested resource was not found.';
    } else {
      userMessage = 'Something went wrong. Please try again.';
    }

    // Attach normalized message to error object for consumption by UI components
    (
      error as AxiosError<BackendErrorPayload> & {
        userMessage: string;
      }
    ).userMessage = userMessage;

    return Promise.reject(error);
  }
);

export default api;