export interface VerificationPopupProps {
  isOpen: boolean;
  onClose: () => void;
  signUpFormData: {
    fullName: string;
    email: string;
    phone_number: string;
    password: string;
    terms: boolean;
  };
}
