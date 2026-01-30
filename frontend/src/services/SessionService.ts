import { Session, SessionLiveFeedback } from '@/interfaces/models/Session';
import { AxiosInstance } from 'axios';

/**
 * Fetches paginated sessions for a scenario.
 */
const getPaginatedSessions = async (
  api: AxiosInstance,
  page: number,
  pageSize: number,
  scenarioId: string
) => {
  try {
    const response = await api.get(`/sessions`, {
      params: {
        page,
        page_size: pageSize,
        scenario_id: scenarioId,
      },
    });
    return response;
  } catch (error) {
    console.error('Error fetching paginated sessions:', error);
    throw error;
  }
};

/**
 * Fetches feedback for a specific session.
 */
export const getSessionFeedback = async (api: AxiosInstance, sessionId: string) => {
  try {
    const response = await api.get(`/sessions/${sessionId}`);
    return response;
  } catch (error) {
    console.error('Error fetching session feedback:', error);
    throw error;
  }
};

/**
 * Clears all sessions (admin/testing utility).
 */
export const clearAllSessions = async (api: AxiosInstance) => {
  try {
    const response = await api.delete(`/sessions/clear-all`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

/**
 * Creates a new session for a scenario.
 */
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

/**
 * Deletes a session by ID.
 */
const deleteSession = async (api: AxiosInstance, sessionId: string) => {
  try {
    const response = await api.delete(`/sessions/${sessionId}`);
    return response;
  } catch (error) {
    console.error('Error deleting session:', error);
    throw error;
  }
};

/**
 * Updates a session's fields.
 */
const updateSession = async (api: AxiosInstance, sessionId: string, session: Partial<Session>) => {
  try {
    const response = await api.put<Session>(`/sessions/${sessionId}`, session);
    return response;
  } catch (error) {
    console.error('Error updating session:', error);
    throw error;
  }
};

/**
 * Posts a session turn with audio and metadata.
 */
const createSessionTurn = async (api: AxiosInstance, sessionTurn: FormData) => {
  try {
    const response = await api.post(`/session-turns`, sessionTurn);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

/**
 * Fetches realtime session data required for live sessions.
 */
const getSessionRealtime = async (api: AxiosInstance, sessionId: string) => {
  try {
    const response = await api.get(`/realtime-sessions/${sessionId}`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

/**
 * Retrieves the SDP answer from the realtime API using an ephemeral key.
 */
const getSdpResponseTextFromRealtimeApi = async (
  ephemeralKey: string,
  offerSdp: string | undefined
) => {
  try {
    const baseUrl = 'https://api.openai.com/v1/realtime';

    const sdpResponse = await fetch(`${baseUrl}/calls`, {
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

/**
 * Fetches live feedback items for a session.
 */
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

/**
 * Session-related API methods.
 */
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
  deleteSession,
};
