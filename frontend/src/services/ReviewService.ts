import { ReviewCreate } from '@/interfaces/models/Review';
import { AxiosInstance } from 'axios';

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
    // eslint-disable-next-line no-restricted-syntax
    console.log('Reviews: ', data);
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
