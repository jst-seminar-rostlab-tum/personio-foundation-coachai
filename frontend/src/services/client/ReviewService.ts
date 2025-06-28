import { ReviewCreate } from '@/interfaces/models/Review';
import { api } from './Api';

const createReview = async (review: ReviewCreate) => {
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
