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

export interface SessionCreate {
  scenarioId: string;
}

export interface SessionPaginated {
  page: number;
  limit: number;
  totalPages: number;
  totalSessions: number;
  sessions: SessionFromPagination[];
}

export interface SessionPaginatedResponse {
  data: SessionPaginated;
}

export interface SessionFromPagination {
  date: string;
  sessionId: string;
  score: number;
  status: SessionStatus;
  title: string;
  summary: string;
  skills: {
    structure: number;
    empathy: number;
    solutionFocus: number;
    clarity: number;
  };
}
