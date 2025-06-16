import { api } from './Api';

const getAdminStats = async () => {
  try {
    const { data } = await api.get(`/admin-stats`);
    return data;
  } catch (error) {
    console.error('Error getting admin stats:', error);
    throw error;
  }
};

export const adminService = {
  getAdminStats,
};
