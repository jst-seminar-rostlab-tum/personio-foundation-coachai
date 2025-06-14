import { Feedback } from '@/interfaces/Feedback';
import { api } from './Api';

export const createFeedback = async (feedback: Feedback) => {
  try {
    const { data } = await api.post('/review', feedback);
    return data;
  } catch (error) {
    console.error('Error creating feedback:', error);
    throw error;
  }
};
