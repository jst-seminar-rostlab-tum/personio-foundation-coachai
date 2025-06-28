import {
  ConversationScenarioFormState,
  ConversationScenarioState,
} from '@/interfaces/state/ConversationScenarioState';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const initialFormState: ConversationScenarioFormState = {
  category: '',
  customCategory: '',
  name: '',
  otherParty: '',
  context: '',
  goal: '',
  difficulty: '',
  emotionalTone: '',
  complexity: '',
  isCustom: false,
};

export const useConversationScenarioStore = create<ConversationScenarioState>()(
  persist(
    (set) => ({
      step: 0,
      formState: initialFormState,
      setStep: (step) => set({ step }),
      updateForm: (newState) =>
        set((state) => ({
          formState: { ...state.formState, ...newState },
        })),
      reset: () => set({ step: 0, formState: initialFormState }),
    }),
    {
      name: 'conversation-scenario-form',
    }
  )
);
