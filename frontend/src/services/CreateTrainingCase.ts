import { TrainingCaseResponse, TrainingCase } from '@/interfaces/TrainingCase';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const createTrainingCase = async (
  trainingCase: TrainingCase
): Promise<TrainingCaseResponse> => {
  try {
    const { data } = await axios.post<TrainingCaseResponse>(`${API_URL}/training-case/`, {
      trainingCase,
    });
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Error creating training case:', error.response?.data || error.message);
    } else {
      console.error('Error creating training case:', error);
    }
    throw error;
  }
};
