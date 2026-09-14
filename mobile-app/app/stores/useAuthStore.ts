/**
 * ATHLETIX — Global Authentication Store
 * mobile-app/app/stores/useAuthStore.ts
 *
 * Singleton state container providing synchronized authentication state across all application screens.
 */

import { create } from 'zustand';

import {
  restoreSession,
  logout as logoutService,
  type AuthUser,
} from '../../services/authService';

interface AuthStore {
  user: AuthUser | null;
  isLoading: boolean;
  isInitialized: boolean;

  /** Restores persisted user session on application mount. */
  initialize: () => Promise<void>;

  /** Refreshes current session data following login or signup events. */
  refresh: () => Promise<void>;

  /** Dispatches backend logout, flushes local storage, and resets active user. */
  logout: () => Promise<void>;
}

// Ensures concurrent initialization calls are deduplicated into a single promise
let initializationPromise: Promise<void> | null = null;

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  isLoading: true,
  isInitialized: false,

  initialize: async (): Promise<void> => {
    if (get().isInitialized) {
      return;
    }

    if (initializationPromise) {
      return initializationPromise;
    }

    initializationPromise = (async () => {
      set({ isLoading: true });

      try {
        const session = await restoreSession();

        set({
          user: session,
          isInitialized: true,
        });
      } catch {
        set({
          user: null,
          isInitialized: true,
        });
      } finally {
        set({ isLoading: false });
        initializationPromise = null;
      }
    })();

    return initializationPromise;
  },

  refresh: async (): Promise<void> => {
    set({ isLoading: true });

    try {
      const session = await restoreSession();

      set({
        user: session,
        isInitialized: true,
      });
    } catch {
      set({
        user: null,
        isInitialized: true,
      });
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async (): Promise<void> => {
    set({ isLoading: true });

    try {
      await logoutService();
    } finally {
      set({
        user: null,
        isLoading: false,
        isInitialized: true,
      });
    }
  },
}));