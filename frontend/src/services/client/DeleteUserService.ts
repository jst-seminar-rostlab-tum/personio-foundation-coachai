import { api } from './Api';

export const deleteUser = async (deleteUserId?: string) => {
  try {
    const url = deleteUserId
      ? `/user-profiles?delete_user_id=${encodeURIComponent(deleteUserId)}`
      : `/user-profiles`;
    const { data } = await api.delete(url);
    return data;
  } catch (error) {
    console.error('Error deleting user ', error);
    throw error;
  }
};
