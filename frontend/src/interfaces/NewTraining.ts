export interface FormState {
  categoryId: string;
  otherParty: string;
  context: string;
  goal: string;
  difficultyLevel: string;
  tone: string;
  complexity: string;
}
export interface ConversationScenarioCreate {
  categoryId: string;
  context: string;
  goal: string;
  otherParty: string;
  difficultyLevel: string;
  tone: string;
  complexity: string;
}

export interface ConversationScenarioCreateResponse {
  scenarioId: string;
  message: string;
}
