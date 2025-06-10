import { SessionError } from '@/interfaces/SessionError';
import api from './Api';

export const sessionService = {
  clearAllSessions: async (userId: string): Promise<{ success: boolean; error?: SessionError }> => {
    try {
      await api.delete(`/session/clear-all/${userId}`);
      return { success: true };
    } catch (err) {
      const error: SessionError = {
        translationKey: 'deleteError',
        status: err.response?.status,
      };

      if (err.response) {
        switch (err.response.status) {
          case 401:
            error.translationKey = 'unauthorizedError';
            break;
          case 403:
            error.translationKey = 'forbiddenError';
            break;
          case 404:
            error.translationKey = 'noSessionsFound';
            break;
          case 500:
            error.translationKey = 'serverError';
            break;
          default:
            error.translationKey = 'deleteError';
            break;
        }
      }

      return { success: false, error };
    }
  },
};
