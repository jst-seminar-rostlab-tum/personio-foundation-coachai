import { api } from './Api';

export const deleteUser = async () => {
  try {
    const { data } = await api.delete(`/user-profiles`);
    return data;
  } catch (error) {
    console.error('Error deleting user ', error);
    throw error;
  }
};
