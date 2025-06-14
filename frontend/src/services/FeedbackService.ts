import { api } from './Api';

export interface Feedback {
  userId: string;
  rating: number;
  comment: string;
}

export const createFeedback = async (data: Feedback) => {
  try {
    const response = await api.post('/review', data);
    return response.data;
  } catch (error) {
    console.error('Error creating feedback:', error);
    throw error;
  }
};
