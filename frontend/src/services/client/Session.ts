import { Session } from '@/interfaces/Session';
import { api } from './Api';

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
  createSession,
  updateSession,
};
