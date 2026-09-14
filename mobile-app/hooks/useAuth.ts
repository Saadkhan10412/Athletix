/**
 * ATHLETIX — Authentication React Hook
 * mobile-app/hooks/useAuth.ts
 *
 * Custom React hook exposing the global authentication context and helper actions to UI screens.
 */

import { useEffect } from 'react';
import { useAuthStore } from '../stores/useAuthStore';

export interface AuthState {
  userId: string | null;
  name: string | null;
  email: string | null;
  role: 'athlete' | 'official' | 'admin' | null;
  isLoading: boolean;

  /** Purges active user session and state across the application. */
  logout: () => Promise<void>;

  /** Revalidates current credentials and updates local user profile. */
  refresh: () => Promise<void>;
}

export function useAuth(): AuthState {
  const user = useAuthStore((state) => state.user);
  const isLoading = useAuthStore((state) => state.isLoading);
  const initialize = useAuthStore((state) => state.initialize);
  const logout = useAuthStore((state) => state.logout);
  const refresh = useAuthStore((state) => state.refresh);

  useEffect(() => {
    void initialize();
  }, [initialize]);

  return {
    userId: user?.userId ?? null,
    name: user?.name ?? null,
    email: user?.email ?? null,
    role: user?.role ?? null,
    isLoading,
    logout,
    refresh,
  };
}
