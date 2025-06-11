import { PaginatedSessionsResponse } from '@/interfaces/Session';
import api from './Api';

export const getPaginatedSessions = async (
  userId: string,
  page: number,
  pageSize: number
): Promise<PaginatedSessionsResponse> => {
  const response = await api.get<PaginatedSessionsResponse>(`/session`, {
    params: {
      page,
      page_size: pageSize,
    },
    headers: {
      'x-user-id': userId,
    },
  });
  if (response.status === 200) {
    return response.data;
  }
  console.error(response);
  throw new Error('Failed to fetch sessions');
};
