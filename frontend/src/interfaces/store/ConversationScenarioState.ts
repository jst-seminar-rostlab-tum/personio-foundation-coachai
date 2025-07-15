import { ContextMode, DifficultyLevelEnums } from '../models/ConversationScenario';

export interface ConversationScenarioFormState {
  category: string;
  situationalFacts: string;
  name: string;
  difficulty: DifficultyLevelEnums;
  persona: string;
  personaDescription: string;
  contextMode: ContextMode;
}

export interface ConversationScenarioState {
  step: number;
  formState: ConversationScenarioFormState;
  setStep: (step: number) => void;
  updateForm: (newState: Partial<ConversationScenarioFormState>) => void;
  reset: () => void;
}
