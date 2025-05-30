export interface PasswordRequirement {
  id: string;
  label: string;
  test: (password: string) => boolean;
}
