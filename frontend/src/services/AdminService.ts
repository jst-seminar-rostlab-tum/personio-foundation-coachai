import { AxiosInstance } from 'axios';

const getAdminStats = async (api: AxiosInstance) => {
  try {
    const { data } = await api.get(`/admin-stats`);
    return data;
  } catch (error) {
    console.error('Error getting admin stats:', error);
    throw error;
  }
};

const updateDailyUserSessionLimit = async (api: AxiosInstance, limit: number) => {
  try {
    const { data } = await api.put(`/app-configs`, {
      key: 'dailyUserSessionLimit',
      value: limit.toString(),
      type: 'int',
    });
    return data;
  } catch (error) {
    console.error('Error updating daily user session limit: ', error);
    throw error;
  }
};

export const adminService = {
  getAdminStats,
  updateDailyUserSessionLimit,
};
