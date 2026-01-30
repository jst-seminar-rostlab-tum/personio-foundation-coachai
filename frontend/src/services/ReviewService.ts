import { ReviewCreate } from '@/interfaces/models/Review';
import { AxiosInstance } from 'axios';

/**
 * Fetches paginated reviews with optional sorting.
 */
const getPaginatedReviews = async (
  api: AxiosInstance,
  page: number,
  pageSize: number | undefined,
  sort: string = 'newest'
) => {
  try {
    const { data } = await api.get(`/reviews`, {
      params: {
        page,
        pageSize,
        sort,
      },
    });
    return data;
  } catch (error) {
    console.error('Error getting review:', error);
    throw error;
  }
};

/**
 * Creates a new review entry.
 */
const createReview = async (api: AxiosInstance, review: ReviewCreate) => {
  try {
    const { data } = await api.post('/reviews', review);
    return data;
  } catch (error) {
    console.error('Error creating review:', error);
    throw error;
  }
};

/**
 * Review-related API methods.
 */
export const reviewService = {
  getPaginatedReviews,
  createReview,
};
