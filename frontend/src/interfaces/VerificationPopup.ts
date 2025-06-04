export interface VerificationPopupProps {
  isOpen: boolean;
  onClose: () => void;
  formData?: {
    fullName: string;
    email: string;
    phoneNumber: string;
    password: string;
    terms: boolean;
  };
}
