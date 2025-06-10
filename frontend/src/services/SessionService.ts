import api from './Api';

export const clearAllSessions = async (userId: string): Promise<{ success: boolean }> => {
  try {
    await api.delete(`/session/clear-all/${userId}`);
    return { success: true };
  } catch (err) {
    console.error(err);
    return { success: false };
  }
};
