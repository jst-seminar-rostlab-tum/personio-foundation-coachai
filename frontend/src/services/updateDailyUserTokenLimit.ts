import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function updateDailyUserTokenLimit(limit: number) {
  const { data } = await axios.put(`${API_URL}/app-config`, {
    dailyUserTokenLimit: limit,
  });
  return data;
}
