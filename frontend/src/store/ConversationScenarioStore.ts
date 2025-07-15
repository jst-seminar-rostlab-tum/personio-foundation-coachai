import {
  ContextModeEnums,
  DifficultyLevelEnums,
  PersonaEnums,
} from '@/interfaces/models/ConversationScenario';
import {
  ConversationScenarioFormState,
  ConversationScenarioState,
} from '@/interfaces/store/ConversationScenarioState';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const initialFormState: ConversationScenarioFormState = {
  category: '',
  situationalFacts: '',
  name: '',
  difficulty: DifficultyLevelEnums.MEDIUM,
  persona: PersonaEnums.POSITIVE,
  personaDescription: '',
  contextMode: ContextModeEnums.DEFAULT,
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
      reset: () =>
        set({
          step: 0,
          formState: initialFormState,
        }),
    }),
    {
      name: 'conversation-scenario-form',
    }
  )
);
