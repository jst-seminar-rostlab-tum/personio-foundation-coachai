export interface SituationStepProps {
  party: string;
  context: string;
  goal: string;
  onPartyChange: (type: string, otherName?: string) => void;
  onContextChange: (context: string) => void;
  onGoalChange: (goal: string) => void;
  isCustom: boolean;
  onCustomCategoryInput: (category: string) => void;
  customCategory: string;
}
