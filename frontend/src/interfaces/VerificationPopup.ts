export interface VerificationPopupProps {
  isOpen: boolean;
  onClose: () => void;
  recipientPhoneNumber: string;
  formData?: {
    fullName: string;
    email: string;
    phoneNumber: string;
    password: string;
    terms: boolean;
  };
}
