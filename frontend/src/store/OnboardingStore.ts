import { OnboardingState } from '@/interfaces/state/OnboardingState';
import { create } from 'zustand';

export const useOnboardingStore = create<OnboardingState>((set) => ({
  step: 0,
  role: '',
  goals: [],
  difficulty: [50],
  conflict: [50],
  conversation: [50],

  setStep: (step) => set({ step }),
  setRole: (role) => set({ role }),
  setGoals: (goals) => set({ goals }),
  setDifficulty: (val) => set({ difficulty: val }),
  setConflict: (val) => set({ conflict: val }),
  setConversation: (val) => set({ conversation: val }),
  reset: () =>
    set({
      step: 0,
      role: '',
      goals: [],
      difficulty: [50],
      conflict: [50],
      conversation: [50],
    }),
}));
