import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function deleteUser(userId: string) {
  try {
    const { data } = await axios.delete(`${API_URL}/user-profiles/${userId}`);
    // eslint-disable-next-line no-restricted-syntax
    console.log('User deleted successfully:', data);
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Error deleting user:', error.response?.data || error.message);
    } else {
      console.error('Error deleting user:', error);
    }
    throw error;
  }
}
