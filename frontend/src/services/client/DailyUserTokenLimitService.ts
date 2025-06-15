import { api } from './Api';

export const updateDailyUserTokenLimit = async (limit: number) => {
  try {
    const { data } = await api.put(`/app-config`, {
      dailyUserTokenLimit: limit,
    });
    return data;
  } catch (error) {
    console.error('Error updating daily user token limit: ', error);
    throw error;
  }
};
