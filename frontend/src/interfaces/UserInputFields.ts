export interface UserPreference {
  label: string;
  options: UserOption[];
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
}

export interface UserConfidenceField {
  title: string;
  minLabel: string;
  maxLabel: string;
  minValue: number;
  maxValue: number;
  value?: number[];
  onChange?: (value: number[]) => void;
}

export interface UserConfidenceFieldProps {
  className?: string;
  difficulty: number[];
  conflict: number[];
  conversation: number[];
  setDifficulty: (value: number[]) => void;
  setConflict: (value: number[]) => void;
  setConversation: (value: number[]) => void;
}

export interface UserOption {
  id: string;
  label: string;
  labelHint?: string;
}

export interface UserRadioQuestion {
  question: string;
  options: UserOption[];
  labelHintAlign?: 'vertical' | 'horizontal';
  selectedValue?: string;
  onValueChange?: (value: string) => void;
}
