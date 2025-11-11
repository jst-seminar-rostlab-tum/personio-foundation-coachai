export interface UserCreate {
  fullName: string;
  email: string;
  phone: string;
  password: string;
  organizationName?: string;
  isNonprofit: boolean;
  // code: string;
}

export interface VerificationCodeCreate {
  phoneNumber: string;
}

export interface VerificationCodeConfirm {
  phoneNumber: string;
  code: string;
}
