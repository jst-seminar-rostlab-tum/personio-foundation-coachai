import { CreateSessionTurnRequest, Session } from '@/interfaces/models/Session';
import { AxiosInstance } from 'axios';

const getPaginatedSessions = async (api: AxiosInstance, page: number, pageSize: number) => {
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
    const response = await api.post<Session>('/session', {
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
    const response = await api.put<Session>(`/session/${sessionId}`, session);
    return response;
  } catch (error) {
    console.error('Error updating session:', error);
    throw error;
  }
};

const createSessionTurn = async (api: AxiosInstance, sessionTurn: CreateSessionTurnRequest) => {
  try {
    const response = await api.post(`/session-turns`, sessionTurn);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getSdpResponseTextFromRealtimeApi = async (
  api: AxiosInstance,
  sessionId: string,
  offerSdp: string | undefined
) => {
  try {
    const realtimeSessionResponse = await api.get(`/realtime-session/${sessionId}`);
    const ephemeralKey = realtimeSessionResponse.data.client_secret.value;

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

export const sessionService = {
  getPaginatedSessions,
  clearAllSessions,
  createSession,
  updateSession,
  getSessionFeedback,
  createSessionTurn,
  getSdpResponseTextFromRealtimeApi,
};
