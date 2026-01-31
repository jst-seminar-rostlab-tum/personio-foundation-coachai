/**
 * Generic user preference selector configuration.
 */
export interface UserPreference<T = string> {
  label: string;
  options: UserOption[];
  value?: T;
  defaultValue?: T;
  placeholder?: string;
  maxSelectedDisclaimer?: string;
  onChange?: (value: T) => void;
}

/**
 * Configuration for a confidence slider field.
 */
export interface UserConfidenceField {
  title: string;
  minLabel: string;
  maxLabel: string;
  minValue: number;
  maxValue: number;
  value?: number[];
  onChange?: (value: number[]) => void;
}

/**
 * Option item used in select and radio inputs.
 */
export interface UserOption {
  id: string;
  label: string;
  labelHint?: string;
}

/**
 * Radio question configuration for onboarding.
 */
export interface UserRadioQuestion {
  question: string;
  options: UserOption[];
  labelHintAlign?: 'vertical' | 'horizontal';
  selectedValue?: string;
  onValueChange?: (value: string) => void;
}
