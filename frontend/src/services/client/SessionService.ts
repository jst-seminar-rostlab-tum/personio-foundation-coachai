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

const createSessionTurn = async (
  sessionId: string,
  speaker: string,
  text: string,
  audioUri: string = '',
  aiEmotion: string = '',
  startOffsetMs: number = 0,
  endOffsetMs: number = 0
) => {
  try {
    const response = await api.post(`/session-turns/`, {
      sessionId,
      speaker,
      text,
      audioUri,
      aiEmotion,
      startOffsetMs,
      endOffsetMs,
    });
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getSdpResponseTextFromRealtimeApi = async (offerSdp: string | undefined) => {
  try {
    const realtimeSessionResponse = await api.get('/realtime-session');
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
  clearAllSessions,
  createSession,
  updateSession,
  getSessionFeedback,
  createSessionTurn,
  getSdpResponseTextFromRealtimeApi,
};
