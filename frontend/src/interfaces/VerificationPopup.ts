export interface VerificationPopupProps {
  isOpen: boolean;
  onClose: () => void;
  signUpFormData: {
    fullName: string;
    email: string;
    phoneNumber: string;
    password: string;
    terms: boolean;
  };
}
