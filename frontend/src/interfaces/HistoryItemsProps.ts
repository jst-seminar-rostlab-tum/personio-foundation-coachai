import { SessionPaginatedResponse } from './Session';

export interface HistoryItemsProps {
  sessionsPromise: Promise<SessionPaginatedResponse>;
}
