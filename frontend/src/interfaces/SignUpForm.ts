export interface SignUpFormProps {
  onSubmit: (values: {
    fullName: string;
    email: string;
    phoneNumber: string;
    password: string;
    terms: boolean;
  }) => void;
}
