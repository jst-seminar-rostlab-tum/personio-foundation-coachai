/**
 * Payload for creating a user during sign-up.
 */
export interface UserCreate {
  fullName: string;
  email: string;
  phone: string;
  verificationCode: string;
  password: string;
  organizationName?: string;
}

/**
 * Payload for requesting a phone verification code.
 */
export interface VerificationCodeCreate {
  phoneNumber: string;
}

/**
 * Payload for confirming a phone verification code.
 */
export interface VerificationCodeConfirm {
  phoneNumber: string;
  code: string;
}
