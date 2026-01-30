import { SessionScores } from './Common';

/**
 * Status values for a session lifecycle.
 */
export enum SessionStatus {
  STARTED = 'started',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

/**
 * Session entity with metadata and scores.
 */
export interface Session {
  id: string;
  scenarioId: string;
  sessionId: string;
  status: SessionStatus;
  title: string;
  summary: string;
  date: string;
  createdAt: string;
  updatedAt: string;
  overallScore: number;
  sessionLengthS: number;
}

/**
 * Paginated sessions response.
 */
export interface SessionPaginated {
  page: number;
  limit: number;
  totalPages: number;
  totalSessions: number;
  sessions: SessionFromPagination[];
}

/**
 * Session summary shape used in pagination lists.
 */
export interface SessionFromPagination {
  date: string;
  sessionId: string;
  score: number;
  status: SessionStatus;
  title: string;
  summary: string;
  skills: SessionScores;
}

/**
 * Payload for creating a session turn.
 */
export interface CreateSessionTurnRequest {
  sessionId: string;
  speaker: MessageSender;
  text: string;
  startOffsetMs: number;
  endOffsetMs: number;
  audioFile: Blob;
}

/**
 * Chat message in a live session.
 */
export interface Message {
  id: number;
  text: string;
  sender: MessageSender;
}

/**
 * Sender roles for messages.
 */
export enum MessageSender {
  USER = 'user',
  ASSISTANT = 'assistant',
}

/**
 * Live feedback item shown during a session.
 */
export interface SessionLiveFeedback {
  id: string;
  heading: string;
  feedbackText: string;
}

/**
 * WebRTC connection status values.
 */
export enum ConnectionStatus {
  Connecting = 'connecting',
  Connected = 'connected',
  Disconnected = 'disconnected',
  Failed = 'failed',
  Closed = 'closed',
  New = 'new',
}
