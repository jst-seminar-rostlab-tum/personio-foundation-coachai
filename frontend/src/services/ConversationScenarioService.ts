import { api } from './Api';

const getPreparation = async (id: string) => {
  try {
    const response = await api.get(`/conversation-scenario/${id}/preparation`);
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const conversationScenarioService = {
  getPreparation,
};
