export interface CreateUserRequest {
  fullName: string;
  email: string;
  phone: string;
  password: string;
  // code: string;
}

export interface SendVerificationCodeRequest {
  phoneNumber: string;
}

export interface VerifyCodeRequest {
  phoneNumber: string;
  code: string;
}
