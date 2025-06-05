import { InputHTMLAttributes } from 'react';

export interface PasswordRequirement {
  id: string;
  label: string;
  test: (password: string) => boolean;
}

export interface PasswordInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  placeholder: string;
  disabled: boolean;
  requirements?: PasswordRequirement[];
}
