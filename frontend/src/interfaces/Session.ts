export interface Session {
  id: string;
  title: string;
  summary: string;
  date: string;
  score: number;
  skills: {
    structure: number;
    empathy: number;
    solutionFocus: number;
    clarity: number;
  };
}

export interface PaginatedSessionsResponse {
  page: number;
  limit: number;
  totalPages: number;
  totalSessions: number;
  sessions: Session[];
}
