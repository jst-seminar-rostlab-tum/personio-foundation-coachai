export interface ConversationScenario {
  categoryId: string;
  difficultyLevel: DifficultyLevelEnums;
  persona: string;
  situationalFacts: string;
  languageCode: string;
  personaName: string;
  scenarioId?: string;
  totalSessions?: number;
  averageScore?: number;
  categoryName?: string;
  lastSessionAt?: string;
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

export enum DifficultyLevelEnums {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard',
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
  personaName: string;
  difficultyLevel: DifficultyLevelEnums;
  categoryId: string;
};
