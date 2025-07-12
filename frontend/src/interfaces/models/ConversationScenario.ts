export interface ConversationScenario {
  categoryId: string;
  customCategoryLabel: string;
  difficultyLevel: string;
  persona: string;
  situationalFacts: string;
  languageCode: string;
}

export interface ConversationCategory {
  id: string;
  name: string;
  iconUri: string;
  defaultContext?: string;
  description?: string;
}

export interface ConversationScenarioResponse {
  message: string;
  scenarioId: string;
}

export interface Persona {
  id: string;
  name: string;
  imageUri: string;
}

export type KeyConcept = {
  header: string;
  value: string;
};

export enum ContextMode {
  DEFAULT = 'default',
  CUSTOM = 'custom',
}

export type ConversationScenarioPreparation = {
  id: string;
  caseId: string;
  objectives: string[];
  documentNames: string[];
  keyConcepts: KeyConcept[];
  prepChecklist: string[];
  status: string;
  createdAt: string;
  updatedAt: string;
  categoryName: string;
  context: ContextMode;
};
