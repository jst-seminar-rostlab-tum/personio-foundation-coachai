import { Review } from '@/interfaces/Review';
import { api } from './Api';

const createReview = async (review: Review) => {
  try {
    const { data } = await api.post('/review', review);
    return data;
  } catch (error) {
    console.error('Error creating review:', error);
    throw error;
  }
};

export const reviewService = {
  createReview,
};
