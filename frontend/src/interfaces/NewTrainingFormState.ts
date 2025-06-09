export interface FormState {
  category: string;
  customCategory: string;
  name: string;
  party: {
    type: string;
    otherName: string;
  };
  context: string;
  goal: string;
  difficulty: string;
  emotionalTone: string;
  complexity: string;
  isCustom: boolean;
}
