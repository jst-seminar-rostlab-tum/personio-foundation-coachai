import {
  ConversationScenarioResponse,
  ConversationScenario,
} from '@/interfaces/ConversationScenario';
import api from './Api';

export const createConversationScenario = async (
  scenario: ConversationScenario
): Promise<ConversationScenarioResponse> => {
  try {
    const { data } = await api.post<ConversationScenarioResponse>('/conversation-scenario/', {
      ...scenario,
    });
    return data;
  } catch (error) {
    console.error('Error creating conversation scenario:', error);
    throw error;
  }
};
