import { AxiosInstance } from 'axios';

const getPaginatedReviews = async (
  api: AxiosInstance,
  page: number,
  pageSize: number,
  sort: string = 'newest'
) => {
  try {
    const { data } = await api.get(`/review`, {
      params: {
        page,
        page_size: pageSize,
        sort,
      },
    });
    return data;
  } catch (error) {
    console.error('Error getting review:', error);
    throw error;
  }
};

export const reviewService = {
  getPaginatedReviews,
};
