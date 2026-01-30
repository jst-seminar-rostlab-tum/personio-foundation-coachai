import { ContextMode, DifficultyLevelEnums } from '../models/ConversationScenario';

/**
 * Form state for creating a conversation scenario.
 */
export interface ConversationScenarioFormState {
  category: string;
  situationalFacts: string;
  name: string;
  difficulty: DifficultyLevelEnums;
  persona: string;
  personaDescription: string;
  contextMode: ContextMode;
}

/**
 * Store state and actions for the conversation scenario flow.
 */
export interface ConversationScenarioState {
  step: number;
  formState: ConversationScenarioFormState;
  setStep: (step: number) => void;
  updateForm: (newState: Partial<ConversationScenarioFormState>) => void;
  reset: () => void;
}
