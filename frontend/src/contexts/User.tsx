'use client';

import { UserProfile } from '@/interfaces/models/UserProfile';
import { createClient } from '@/lib/supabase/client';
import { logoutUser } from '@/lib/supabase/logout';
import { api } from '@/services/ApiClient';
import { UserProfileService } from '@/services/UserProfileService';
import { useRouter } from 'next/navigation';
import { createContext, useContext, useEffect, useState } from 'react';

const UserContext = createContext<UserProfile | undefined>(undefined);

export function UserContextProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | undefined>(undefined);
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      router.refresh();
    });

    return () => subscription.unsubscribe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  useEffect(() => {
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

export function useUser() {
  return useContext(UserContext);
}
