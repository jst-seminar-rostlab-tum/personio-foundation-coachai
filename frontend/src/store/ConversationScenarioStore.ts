import {
  ConversationScenarioFormState,
  ConversationScenarioState,
} from '@/interfaces/store/ConversationScenarioState';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const initialFormState: ConversationScenarioFormState = {
  category: '',
  customCategory: '',
  situationalFacts: '',
  name: '',
  difficulty: '',
  persona: '',
  personaDescription: '',
  isCustom: false,
};

const initialContextMode: 'default' | 'custom' = 'default';
const initialCustomContext = '';

export const useConversationScenarioStore = create<ConversationScenarioState>()(
  persist(
    (set) => ({
      step: 0,
      formState: initialFormState,
      contextMode: initialContextMode,
      customContext: initialCustomContext,
      setStep: (step) => set({ step }),
      updateForm: (newState) =>
        set((state) => ({
          formState: { ...state.formState, ...newState },
        })),
      setContextMode: (mode) => set({ contextMode: mode }),
      setCustomContext: (text) => set({ customContext: text }),
      reset: () =>
        set({
          step: 0,
          formState: initialFormState,
          contextMode: initialContextMode,
          customContext: initialCustomContext,
        }),
    }),
    {
      name: 'conversation-scenario-form',
    }
  )
);
