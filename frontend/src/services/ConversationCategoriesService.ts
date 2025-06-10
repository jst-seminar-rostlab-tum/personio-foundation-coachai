import { ConversationCategory } from '@/interfaces/ConversationCategory';
import api from './Api';

export const getConversationCategories = async (): Promise<ConversationCategory[]> => {
  try {
    const { data } = await api.get<ConversationCategory[]>('/conversation-categories/');
    return data;
  } catch (error) {
    console.error('Error fetching conversation categories:', error);
    throw error;
  }
};
