import { api } from './Api';

const updateDailyUserTokenLimit = async (limit: number) => {
  try {
    const { data } = await api.put(`/app-config`, {
      key: 'dailyUserTokenLimit',
      value: limit.toString(),
      type: 'int',
    });
    return data;
  } catch (error) {
    console.error('Error updating daily user token limit: ', error);
    throw error;
  }
};

export const adminService = {
  updateDailyUserTokenLimit,
};
