'use client';

import { UserProfile } from '@/interfaces/models/UserProfile';
import { createClient } from '@/lib/supabase/client';
import { logoutUser } from '@/lib/supabase/logout';
import { api } from '@/services/ApiClient';
import { UserProfileService } from '@/services/UserProfileService';
import { useRouter } from 'next/navigation';
import { createContext, useContext, useEffect, useState } from 'react';

/**
 * Holds the current user profile for the session.
 */
const UserContext = createContext<UserProfile | undefined>(undefined);

/**
 * Props for the user context provider.
 */
interface UserContextProviderProps {
  children: React.ReactNode;
}

/**
 * Provides the current user profile and refreshes on auth changes.
 */
export function UserContextProvider({ children }: UserContextProviderProps) {
  const [user, setUser] = useState<UserProfile | undefined>(undefined);
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    /**
     * Refreshes routes when the auth session changes.
     */
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      router.refresh();
    });

    return () => subscription.unsubscribe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  useEffect(() => {
    /**
     * Loads the current user profile or logs out on error.
     */
    const fetchUser = async () => {
      try {
        const userProfile = await UserProfileService.getUserProfile(api);
        setUser(userProfile);
      } catch (err) {
        console.error('Error fetching user profile:', err);
        await logoutUser(createClient);
      }
    };

    fetchUser();
  }, [router]);

  return <UserContext.Provider value={user}>{children}</UserContext.Provider>;
}

/**
 * Hook to access the current user context.
 */
export function useUser() {
  return useContext(UserContext);
}
