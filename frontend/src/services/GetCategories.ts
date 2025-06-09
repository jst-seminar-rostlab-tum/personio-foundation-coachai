import { ConversationCategory } from '@/interfaces/ConversationCategory';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const getConversationCategories = async (): Promise<ConversationCategory[]> => {
  try {
    const { data } = await axios.get<ConversationCategory[]>(`${API_URL}/conversation-categories/`);
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(
        'Error fetching conversation categories:',
        error.response?.data || error.message
      );
    } else {
      console.error('Error fetching conversation categories:', error);
    }
    throw error;
  }
};
