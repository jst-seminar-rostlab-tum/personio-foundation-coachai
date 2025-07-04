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

export interface ConversationCategory {
  id: string;
  name: string;
  iconUri: string;
  defaultContext?: string;
  defaultGoal?: string;
  defaultOtherParty?: string;
  isCustom?: boolean;
  description?: string;
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
