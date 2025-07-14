export interface ConversationScenario {
  categoryId: string;
  difficultyLevel: string;
  persona: string;
  situationalFacts: string;
  languageCode: string;
  personaName: string;
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

export enum PersonaEnums {
  POSITIVE = 'positive',
  ANGRY = 'angry',
  SHY = 'shy',
  CASUAL = 'casual',
  SAD = 'sad',
}

export enum ContextModeEnums {
  DEFAULT = 'default',
  CUSTOM = 'custom',
}

export type ContextMode = ContextModeEnums.CUSTOM | ContextModeEnums.DEFAULT;

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
  situationalFacts: string;
  persona: string;
};
