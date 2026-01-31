import { Document } from './Document';

/**
 * Core conversation scenario entity.
 */
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

/**
 * Metadata for a conversation category.
 */
export interface ConversationCategory {
  id: string;
  name: string;
  iconUri: string;
  defaultContext?: string;
  description?: string;
}

/**
 * Response payload after creating a scenario.
 */
export interface ConversationScenarioResponse {
  message: string;
  scenarioId: string;
}

/**
 * Persona configuration for scenario creation.
 */
export interface Persona {
  id: string;
  name: string;
  imageUri: string;
}

/**
 * Key concept item used in preparation details.
 */
export type KeyConcept = {
  header: string;
  value: string;
};

/**
 * Supported persona identifiers.
 */
export enum PersonaEnums {
  POSITIVE = 'positive',
  ANGRY = 'angry',
  SHY = 'shy',
  CASUAL = 'casual',
  SAD = 'sad',
}

/**
 * Supported context modes for scenario setup.
 */
export enum ContextModeEnums {
  DEFAULT = 'default',
  CUSTOM = 'custom',
}

/**
 * Supported difficulty levels for scenarios.
 */
export enum DifficultyLevelEnums {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard',
}

/**
 * Union type for context modes.
 */
export type ContextMode = ContextModeEnums.CUSTOM | ContextModeEnums.DEFAULT;

/**
 * Preparation data returned for a scenario.
 */
export type ConversationScenarioPreparation = {
  id: string;
  caseId: string;
  objectives: string[];
  documents: Document[];
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
