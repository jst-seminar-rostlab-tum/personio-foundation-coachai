import {
  ConversationScenarioCreate,
  ConversationScenarioCreateResponse,
} from '@/interfaces/NewTraining';
import { api } from './Api';

export const createConversationScenario = async (
  data: ConversationScenarioCreate
): Promise<ConversationScenarioCreateResponse> => {
  const response = await api.post('/conversation-scenario/', data);
  return response.data;
};
