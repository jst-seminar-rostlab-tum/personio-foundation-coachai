import { api } from './Api';

const getPaginatedSessions = async (page: number, pageSize: number) => {
  try {
    const response = await api.get(`/session`, {
      params: {
        page,
        page_size: pageSize,
      },
    });
    return response;
  } catch (error) {
    console.error('Error fetching paginated sessions:', error);
    throw error;
  }
};

export const sessionService = {
  getPaginatedSessions,
};
