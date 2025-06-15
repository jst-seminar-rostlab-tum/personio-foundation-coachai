import { Session } from '@/interfaces/Session';
import { api } from './Api';

export const getSessionFeedback = async (sessionId: string) => {
  try {
    const response = await api.get(`/session/${sessionId}`);
    return response;
  } catch (error) {
    console.error('Error fetching session feedback:', error);
    throw error;
  }
};

export const clearAllSessions = async () => {
  try {
    const response = await api.delete(`/session/clear-all`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createSession = async (scenarioId: string) => {
  try {
    const response = await api.post<Session>('/session/', {
      scenarioId,
    });
    return response;
  } catch (error) {
    console.error('Error creating conversation scenario:', error);
    throw error;
  }
};

const updateSession = async (sessionId: string, session: Partial<Session>) => {
  try {
    const response = await api.put<Session>(`/session/${sessionId}/`, session);
    return response;
  } catch (error) {
    console.error('Error updating session:', error);
    throw error;
  }
};

export const sessionService = {
  clearAllSessions,
  createSession,
  updateSession,
  getSessionFeedback,
};
