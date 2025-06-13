import { useState } from 'react';
import { deleteUser } from '@/services/deleteUser';

export function useDeleteUser() {
  const [loading, setLoading] = useState(false);

  async function handleDeleteUser(userId: string) {
    setLoading(true);
    try {
      await deleteUser(userId);
    } catch (error) {
      console.error({ error });
    } finally {
      setLoading(false);
    }
  }

  return { handleDeleteUser, loading };
}
