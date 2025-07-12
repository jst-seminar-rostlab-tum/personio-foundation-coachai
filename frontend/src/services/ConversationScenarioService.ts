import {
  ConversationScenarioResponse,
  ConversationScenario,
} from '@/interfaces/models/ConversationScenario';
import { AxiosInstance } from 'axios';

const getConversationCategories = async (api: AxiosInstance) => {
  try {
    const response = await api.get('/conversation-categories');
    return response;
  } catch (error) {
    console.error('Error fetching conversation categories:', error);
    throw error;
  }
};

const createConversationScenario = async (api: AxiosInstance, scenario: ConversationScenario) => {
  try {
    const response = await api.post<ConversationScenarioResponse>('/conversation-scenarios', {
      ...scenario,
      persona: '', // Temporary fix until new version of create conversation scenario is ready
      situationalFacts: '', // Temporary fix until new version of create conversation scenario is ready
    });
    return response;
  } catch (error) {
    console.error('Error creating conversation scenario:', error);
    throw error;
  }
};

const getPreparation = async (api: AxiosInstance, id: string) => {
  try {
    const response = await api.get(`/conversation-scenarios/${id}/preparation`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const conversationScenarioService = {
  getConversationCategories,
  getPreparation,
  createConversationScenario,
};
