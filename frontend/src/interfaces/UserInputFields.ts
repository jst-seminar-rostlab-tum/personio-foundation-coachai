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
