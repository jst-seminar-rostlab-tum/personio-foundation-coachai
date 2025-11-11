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

const updateDefaultDailyUserSessionLimit = async (api: AxiosInstance, limit: number) => {
  try {
    const { data } = await api.put(`/app-configs`, {
      key: 'defaultDailyUserSessionLimit',
      value: limit.toString(),
      type: 'int',
    });
    return data;
  } catch (error) {
    console.error('Error updating default daily user session limit: ', error);
    throw error;
  }
};

export const adminService = {
  getAdminStats,
  updateDefaultDailyUserSessionLimit,
};
