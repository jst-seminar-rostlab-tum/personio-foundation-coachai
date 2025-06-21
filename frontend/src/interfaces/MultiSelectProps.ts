import { UserOption } from './UserInputFields';

export interface MultiSelectProps {
  options: UserOption[];
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  maxSelectedDisclaimer?: string;
  maxSelected?: number;
}
