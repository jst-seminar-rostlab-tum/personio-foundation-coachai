/**
 * Store state and actions for onboarding.
 */
export interface OnboardingState {
  step: number;
  role: string;
  goals: string[];
  difficulty: number[];
  conflict: number[];
  conversation: number[];

  setStep: (step: number) => void;
  setRole: (role: string) => void;
  setGoals: (goals: string[]) => void;
  setDifficulty: (val: number[]) => void;
  setConflict: (val: number[]) => void;
  setConversation: (val: number[]) => void;
  reset: () => void;
}
