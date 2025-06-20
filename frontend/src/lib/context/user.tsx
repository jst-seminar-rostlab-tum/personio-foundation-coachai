'use client';

import { UserProfile } from '@/interfaces/UserProfile';
import { createContext, useContext } from 'react';

const UserContext = createContext<UserProfile>(undefined!);

export function UserContextProvider({
  children,
  user,
}: {
  children: React.ReactNode;
  user: UserProfile;
}) {
  return <UserContext.Provider value={user}>{children}</UserContext.Provider>;
}

export function useUser() {
  return useContext(UserContext);
}
