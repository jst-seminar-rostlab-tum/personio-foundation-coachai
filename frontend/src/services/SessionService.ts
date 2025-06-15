import { Session } from '@/interfaces/Session';
import { AxiosInstance } from 'axios';

export const getPaginatedSessions = async (api: AxiosInstance, page: number, pageSize: number) => {
  try {
    const response = await api.get(`/session`, {
      params: {
        page,
        page_size: pageSize,
      },
    });
    return response;
  } catch (error) {
    console.error('Error fetching paginated sessions:', error);
    throw error;
  }
};

export const getSessionFeedback = async (api: AxiosInstance, sessionId: string) => {
  try {
    const response = await api.get(`/session/${sessionId}`);
    return response;
  } catch (error) {
    console.error('Error fetching session feedback:', error);
    throw error;
  }
};

export const clearAllSessions = async (api: AxiosInstance) => {
  try {
    const response = await api.delete(`/session/clear-all`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createSession = async (api: AxiosInstance, scenarioId: string) => {
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

const updateSession = async (api: AxiosInstance, sessionId: string, session: Partial<Session>) => {
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
