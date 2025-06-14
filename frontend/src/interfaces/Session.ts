export enum SessionStatus {
  STARTED = 'started',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
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
