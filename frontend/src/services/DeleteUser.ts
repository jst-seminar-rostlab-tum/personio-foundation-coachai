import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function deleteUser(userId: string) {
  try {
    const { data } = await axios.delete(`${API_URL}/user-profiles/${userId}`);
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
