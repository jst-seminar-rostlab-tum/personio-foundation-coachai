export interface UserCreate {
  fullName: string;
  email: string;
  phone: string;
  verificationCode: string;
  password: string;
  organizationName?: string;
}

export interface VerificationCodeCreate {
  phoneNumber: string;
}

export interface VerificationCodeConfirm {
  phoneNumber: string;
  code: string;
}
