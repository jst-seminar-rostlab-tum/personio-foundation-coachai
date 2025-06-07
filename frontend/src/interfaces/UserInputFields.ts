export interface UserPreferenceOption {
  code: string;
  name: string;
}

export interface UserPreference {
  label: string;
  options: UserPreferenceOption[];
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
  onChange?: (value: number[]) => void;
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
