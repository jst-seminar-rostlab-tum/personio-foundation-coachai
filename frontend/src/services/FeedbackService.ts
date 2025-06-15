import { Feedback } from '@/interfaces/Feedback';
import { AxiosInstance } from 'axios';

export const createFeedback = async (api: AxiosInstance, feedback: Feedback) => {
  try {
    const { data } = await api.post('/review', feedback);
    return data;
  } catch (error) {
    console.error('Error creating feedback:', error);
    throw error;
  }
};
