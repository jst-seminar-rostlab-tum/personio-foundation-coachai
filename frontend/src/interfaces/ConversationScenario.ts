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
}

export interface ConversationScenarioResponse {
  message: string;
  scenarioId: string;
}

export type KeyConcept = {
  header: string;
  value: string;
};

export type ConversationScenarioPreparation = {
  id: string;
  caseId: string;
  objectives: string[];
  keyConcepts: KeyConcept[];
  prepChecklist: string[];
  status: string;
  createdAt: string;
  updatedAt: string;
  categoryName: string;
  context: string;
};
