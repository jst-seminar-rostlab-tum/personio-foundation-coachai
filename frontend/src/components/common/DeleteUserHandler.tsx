import { useState } from 'react';
import { deleteUser } from '@/services/client/DeleteUserService';

export function useDeleteUser() {
  const [loading, setLoading] = useState(false);

  async function handleDeleteUser(deleteUserId?: string) {
    setLoading(true);
    try {
      await deleteUser(deleteUserId);
    } catch (error) {
      console.error({ error });
    } finally {
      setLoading(false);
    }
  }

  return { handleDeleteUser, loading };
}
