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

export const SessionService = {
  clearAllSessions,
};

export const createSessionTurn = async (
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
