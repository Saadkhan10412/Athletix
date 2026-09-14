/**
 * ATHLETIX — Global Authentication Zustand Store
 * mobile-app/stores/useAuthStore.ts
 *
 * Centralized state container managing user authentication and active session lifecycle.
 *
 * Core Responsibilities:
 * - Session Restoration: Rehydrates user profile and JWT token from persistent storage upon app startup.
 * - Reactive Auth State: Provides components with reactive access to `user`, `isLoading`, and `isInitialized`.
 * - State Cleardown: Coordinates with the auth service to safely purge session credentials on logout.
 */

import { create } from 'zustand';
import {
  type AuthUser,
  restoreSession,
  logout as authLogout,
} from '../services/authService';

export interface AuthStoreState {
  user: AuthUser | null;
  isLoading: boolean;
  isInitialized: boolean;
  setUser: (user: AuthUser | null) => void;
  initialize: () => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

export const useAuthStore = create<AuthStoreState>((set, get) => ({
  user: null,
  isLoading: true,
  isInitialized: false,

  setUser: (user: AuthUser | null) => {
    set({ user });
  },

  /**
   * Initializes auth state by loading persisted credentials on app launch.
   */
  initialize: async () => {
    if (get().isInitialized) {
      return;
    }
    try {
      set({ isLoading: true });
      const user = await restoreSession();
      set({ user, isLoading: false, isInitialized: true });
    } catch {
      set({ user: null, isLoading: false, isInitialized: true });
    }
  },

  /**
   * Clears active user session locally and invalidates backend tokens.
   */
  logout: async () => {
    try {
      set({ isLoading: true });
      await authLogout();
    } finally {
      set({ user: null, isLoading: false });
    }
  },

  /**
   * Refreshes active user state from storage or remote session.
   */
  refresh: async () => {
    try {
      set({ isLoading: true });
      const user = await restoreSession();
      set({ user, isLoading: false });
    } catch {
      set({ user: null, isLoading: false });
    }
  },
}));
