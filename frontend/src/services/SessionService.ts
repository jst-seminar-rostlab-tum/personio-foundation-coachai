import { api } from './Api';

export const clearAllSessions = async () => {
  try {
    const response = await api.delete(`/session/clear-all/`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const SessionService = {
  clearAllSessions,
};
