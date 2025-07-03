import { SessionScores } from './Common';

export enum SessionStatus {
  STARTED = 'started',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Session {
  id: string;
  scenarioId: string;
  status: SessionStatus;
  title: string;
  summary: string;
  date: string;
  createdAt: string;
  updatedAt: string;
}

export interface SessionPaginated {
  page: number;
  limit: number;
  totalPages: number;
  totalSessions: number;
  sessions: SessionFromPagination[];
}

export interface SessionFromPagination {
  date: string;
  sessionId: string;
  score: number;
  status: SessionStatus;
  title: string;
  summary: string;
  skills: SessionScores;
}

export interface CreateSessionTurnRequest {
  sessionId: string;
  speaker: MessageSender;
  text: string;
  startOffsetMs: number;
  audioFile: Blob;
}

export interface Message {
  id: number;
  text: string;
  sender: MessageSender;
  startOffsetMs: number;
}

export enum MessageSender {
  USER = 'user',
  ASSISTANT = 'assistant',
}
