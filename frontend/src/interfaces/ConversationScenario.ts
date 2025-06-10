export interface ConversationScenario {
  userId: string;
  categoryId: string;
  customCategoryLabel: string;
  context: string;
  goal: string;
  otherParty: string;
  difficultyId: string;
  tone: string;
  complexity: string;
  status?: string;
}

export interface ConversationScenarioResponse {
  id: string;
  userId: string;
  categoryId: string;
  customCategoryLabel: string;
  context: string;
  goal: string;
  otherParty: string;
  difficultyId: string;
  tone: string;
  complexity: string;
  status: string;
  createdAt: string;
  updatedAt: string;
}
