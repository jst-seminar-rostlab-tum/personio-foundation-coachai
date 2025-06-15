export interface ConversationScenario {
  categoryId: string;
  customCategoryLabel: string;
  context: string;
  goal: string;
  otherParty: string;
  difficultyLevel: string;
  tone: string;
  complexity: string;
  status?: string;
  languageCode: string;
}

export interface ConversationScenarioResponse {
  message: string;
  scenarioId: string;
}
