import { ReviewCreate } from '@/interfaces/models/Review';
import { AxiosInstance } from 'axios';

const getPaginatedReviews = async (
  api: AxiosInstance,
  page: number,
  pageSize: number,
  sort: string = 'newest'
) => {
  try {
    const { data } = await api.get(`/reviews`, {
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

const createReview = async (api: AxiosInstance, review: ReviewCreate) => {
  try {
    const { data } = await api.post('/reviews', review);
    return data;
  } catch (error) {
    console.error('Error creating review:', error);
    throw error;
  }
};

export const reviewService = {
  getPaginatedReviews,
  createReview,
};
