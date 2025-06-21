import { ConversationScenarioFormState } from '@/interfaces/ConversationScenarioFormState';

export interface ConversationScenarioState {
  step: number;
  formState: ConversationScenarioFormState;
  setStep: (step: number) => void;
  updateForm: (newState: Partial<ConversationScenarioFormState>) => void;
  reset: () => void;
}
