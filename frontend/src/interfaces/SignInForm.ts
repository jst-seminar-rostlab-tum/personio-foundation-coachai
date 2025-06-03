export interface SignInFormProps {
  onSubmit: (values: { email: string; password: string }) => void;
}

export interface SignInCredentials {
  email: string;
  password: string;
}
