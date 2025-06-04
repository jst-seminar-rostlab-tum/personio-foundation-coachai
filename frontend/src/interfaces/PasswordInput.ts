export interface PasswordRequirement {
  id: string;
  label: string;
  test: (password: string) => boolean;
}

export interface PasswordInputProps {
  placeholder: string;
  disabled: boolean;
  requirements?: PasswordRequirement[];
}
