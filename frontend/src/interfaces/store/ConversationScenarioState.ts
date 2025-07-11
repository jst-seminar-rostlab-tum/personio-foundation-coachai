export interface ConversationScenarioFormState {
  category: string;
  customCategory: string;
  situationalFacts: string;
  name: string;
  difficulty: string;
  persona: string;
  personaDescription: string;
  isCustom: boolean;
}

export interface ConversationScenarioState {
  step: number;
  formState: ConversationScenarioFormState;
  contextMode: 'default' | 'custom';
  customContext: string;
  setStep: (step: number) => void;
  updateForm: (newState: Partial<ConversationScenarioFormState>) => void;
  setContextMode: (mode: 'default' | 'custom') => void;
  setCustomContext: (text: string) => void;
  reset: () => void;
}
