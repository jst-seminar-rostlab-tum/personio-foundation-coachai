import {
  ConversationScenarioResponse,
  ConversationScenario,
} from '@/interfaces/models/ConversationScenario';
import { AxiosInstance } from 'axios';

/**
 * Fetches paginated conversation scenarios.
 */
const getConversationScenarios = async (api: AxiosInstance, page: number, pageSize: number) => {
  try {
    const response = await api.get('/conversation-scenarios', {
      params: {
        page_size: pageSize,
        page,
      },
    });
    return response;
  } catch (error) {
    console.error('Error fetching conversation scenarios:', error);
    throw error;
  }
};

/**
 * Fetches a single conversation scenario by ID.
 */
const getConversationScenario = async (api: AxiosInstance, id: string) => {
  try {
    const response = await api.get(`/conversation-scenarios/${id}`);
    return response;
  } catch (error) {
    console.error('Error fetching conversation scenario:', error);
    throw error;
  }
};

/**
 * Creates a new conversation scenario.
 */
const createConversationScenario = async (
  api: AxiosInstance,
  scenario: ConversationScenario,
  isAdvisedScenario: boolean = false
) => {
  try {
    const response = await api.post<ConversationScenarioResponse>(
      '/conversation-scenarios',
      scenario,
      {
        params: { advised_scenario: isAdvisedScenario },
      }
    );
    return response;
  } catch (error) {
    console.error('Error creating conversation scenario:', error);
    throw error;
  }
};

/**
 * Fetches preparation data for a scenario.
 */
const getPreparation = async (api: AxiosInstance, id: string) => {
  try {
    const response = await api.get(`/conversation-scenarios/${id}/preparation`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

/**
 * Deletes a conversation scenario by ID.
 */
const deleteConversationScenario = async (api: AxiosInstance, id: string) => {
  try {
    const response = await api.delete(`/conversation-scenarios/${id}`);
    return response;
  } catch (error) {
    console.error('Error deleting conversation scenario:', error);
    throw error;
  }
};

/**
 * Conversation scenario API methods.
 */
export const conversationScenarioService = {
  getPreparation,
  createConversationScenario,
  getConversationScenarios,
  getConversationScenario,
  deleteConversationScenario,
};
