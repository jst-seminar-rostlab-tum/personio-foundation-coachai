import { OnboardingState } from '@/interfaces/store/OnboardingState';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Zustand store for onboarding progress and responses.
 */
export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set) => ({
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
    }),
    { name: 'onboarding-data' }
  )
);
