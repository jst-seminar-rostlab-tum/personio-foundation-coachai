import {
  ConversationScenarioResponse,
  ConversationScenario,
} from '@/interfaces/ConversationScenario';
import { api } from './Api';

const createConversationScenario = async (scenario: ConversationScenario) => {
  try {
    const response = await api.post<ConversationScenarioResponse>('/conversation-scenario', {
      ...scenario,
    });
    return response;
  } catch (error) {
    console.error('Error creating conversation scenario:', error);
    throw error;
  }
};

const getPreparation = async (id: string) => {
  try {
    const response = await api.get(`/conversation-scenario/${id}/preparation`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
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
  getPreparation,
  createConversationScenario,
  getConversationCategories,
};
