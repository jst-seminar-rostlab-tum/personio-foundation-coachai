export interface CreateUserRequest {
  full_name: string;
  email: string;
  phone: string;
  password: string;
  // code: string;
}

export interface SendVerificationCodeRequest {
  phone_number: string;
}

export interface VerifyCodeRequest {
  phone_number: string;
  code: string;
}
