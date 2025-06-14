import { api } from './Api';

export const createNewTraining = async (data: any) => {
  try {
    const response = await api.post('/conversation-scenario/', data);
    return response.data;
  } catch (error) {
    console.error('Error creating new training:', error);
    throw error;
  }
};
