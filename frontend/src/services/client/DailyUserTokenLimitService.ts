import { api } from './Api';

export const updateDailyUserTokenLimit = async (limit: number) => {
  const { data } = await api.put(`/app-config`, {
    dailyUserTokenLimit: limit,
  });
  return data;
};
