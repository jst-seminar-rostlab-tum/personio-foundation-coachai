import api from './Api';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function deleteUser(userId: string) {
  try {
    const { data } = await api.delete(`${API_URL}/user-profiles/${userId}`);
    return data;
  } catch (error) {
    if (
      error &&
      typeof error === 'object' &&
      'response' in error &&
      error.response &&
      typeof error.response === 'object' &&
      'data' in error.response
    ) {
      console.error(
        'Error deleting user:',
        (error.response as { data?: unknown })?.data || (error as { message?: string })?.message
      );
    } else {
      console.error('Error deleting user:', error);
    }
    throw error;
  }
}
