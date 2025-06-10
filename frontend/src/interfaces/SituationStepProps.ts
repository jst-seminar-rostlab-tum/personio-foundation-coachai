export interface SituationStepProps {
  otherParty: string;
  context: string;
  goal: string;
  onPartyChange: (otherParty: string) => void;
  onContextChange: (context: string) => void;
  onGoalChange: (goal: string) => void;
  isCustom: boolean;
  onCustomCategoryInput: (category: string) => void;
  customCategory: string;
}
