export interface ConversationScenarioFormState {
  category: string;
  customCategory: string;
  name: string;
  otherParty: string;
  context: string;
  goal: string;
  difficulty: string;
  complexity: string;
  persona: string;
  isCustom: boolean;
}

export interface ConversationScenarioState {
  step: number;
  formState: ConversationScenarioFormState;
  setStep: (step: number) => void;
  updateForm: (newState: Partial<ConversationScenarioFormState>) => void;
  reset: () => void;
}
