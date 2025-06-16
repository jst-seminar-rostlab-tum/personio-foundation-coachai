'use client';

import { UserProfile } from '@/interfaces/UserProfile';
import { createContext, useContext } from 'react';

const UserContext = createContext<UserProfile | null>(null);

export function UserContextProvider({
  children,
  user,
}: {
  children: React.ReactNode;
  user: UserProfile | null;
}) {
  return <UserContext.Provider value={user}>{children}</UserContext.Provider>;
}

export function useUser() {
  return useContext(UserContext);
}
