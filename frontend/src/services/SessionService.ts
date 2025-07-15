import { Session, SessionLiveFeedback } from '@/interfaces/models/Session';
import { AxiosInstance } from 'axios';

const getPaginatedSessions = async (api: AxiosInstance, page: number, pageSize: number) => {
  try {
    const response = await api.get(`/sessions`, {
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
    const response = await api.get(`/sessions/${sessionId}`);
    return response;
  } catch (error) {
    console.error('Error fetching session feedback:', error);
    throw error;
  }
};

export const clearAllSessions = async (api: AxiosInstance) => {
  try {
    const response = await api.delete(`/sessions/clear-all`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createSession = async (api: AxiosInstance, scenarioId: string) => {
  try {
    const response = await api.post<Session>('/sessions', {
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
    const response = await api.put<Session>(`/sessions/${sessionId}`, session);
    return response;
  } catch (error) {
    console.error('Error updating session:', error);
    throw error;
  }
};

const createSessionTurn = async (api: AxiosInstance, sessionTurn: FormData) => {
  try {
    const response = await api.post(`/session-turns`, sessionTurn);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getSessionRealtime = async (api: AxiosInstance, sessionId: string) => {
  try {
    const response = await api.get(`/realtime-sessions/${sessionId}`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getSdpResponseTextFromRealtimeApi = async (
  ephemeralKey: string,
  offerSdp: string | undefined
) => {
  try {
    const baseUrl = 'https://api.openai.com/v1/realtime';
    const modelId = 'gpt-4o-realtime-preview-2025-06-03';

    const sdpResponse = await fetch(`${baseUrl}?model=${modelId}`, {
      method: 'POST',
      body: offerSdp,
      headers: {
        Authorization: `Bearer ${ephemeralKey}`,
        'Content-Type': 'application/sdp',
      },
    });
    return sdpResponse.text();
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getSessionLiveFeedback = async (api: AxiosInstance, sessionId: string) => {
  try {
    const response = await api.get<SessionLiveFeedback[]>(`/live-feedback/session/${sessionId}`, {
      params: { limit: 5 },
    });
    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const sessionService = {
  getPaginatedSessions,
  clearAllSessions,
  createSession,
  updateSession,
  getSessionFeedback,
  getSessionLiveFeedback,
  createSessionTurn,
  getSdpResponseTextFromRealtimeApi,
  getSessionRealtime,
};
