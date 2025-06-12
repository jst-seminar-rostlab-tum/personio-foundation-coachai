import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getAdminStats() {
  const { data } = await axios.get(`${API_URL}/admin-stats`);
  return data;
}
