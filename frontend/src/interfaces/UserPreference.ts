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
