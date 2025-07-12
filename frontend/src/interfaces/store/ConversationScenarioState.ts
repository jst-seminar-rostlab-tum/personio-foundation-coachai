import { ContextMode } from '../models/ConversationScenario';

export interface ConversationScenarioFormState {
  category: string;
  customCategory: string;
  situationalFacts: string;
  name: string;
  difficulty: string;
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
