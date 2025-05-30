export interface SignInFormProps {
  onSubmit: (values: { email: string; password: string }) => void;
}
