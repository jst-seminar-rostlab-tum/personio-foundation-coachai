import { useState } from 'react';
import { deleteUser } from '@/services/client/DeleteUserService';

export function useDeleteUser() {
  const [loading, setLoading] = useState(false);

  async function handleDeleteUser() {
    setLoading(true);
    try {
      await deleteUser();
    } catch (error) {
      console.error({ error });
    } finally {
      setLoading(false);
    }
  }

  return { handleDeleteUser, loading };
}
