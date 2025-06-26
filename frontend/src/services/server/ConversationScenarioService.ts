import { api } from './Api';

const getConversationCategories = async () => {
  try {
    const response = await api.get('/conversation-categories');
    return response;
  } catch (error) {
    console.error('Error fetching conversation categories:', error);
    throw error;
  }
};

export const conversationScenarioService = {
  getConversationCategories,
};
