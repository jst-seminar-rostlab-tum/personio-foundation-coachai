export interface SituationStepProps {
  party: {
    type: string;
    otherName?: string;
  };
  context: string;
  goal: string;
  onPartyChange: (type: string, otherName?: string) => void;
  onContextChange: (context: string) => void;
  onGoalChange: (goal: string) => void;
  category: string;
  onCustomCategoryInput: (category: string) => void;
  customCategory: string;
}
