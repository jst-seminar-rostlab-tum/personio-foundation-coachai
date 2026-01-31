import { UserCreate, VerificationCodeCreate } from '@/interfaces/models/Auth';
import { AxiosInstance } from 'axios';

/**
 * Creates a user account in the backend.
 */
const signUpUser = async (api: AxiosInstance, data: UserCreate) => {
  const response = await api.post('/auth/sign-up-user', data);
  return response.data;
};

/**
 * Sends a phone verification code for signup.
 */
const sendVerificationCode = async (api: AxiosInstance, data: VerificationCodeCreate) => {
  const response = await api.post('/auth/send-phone-verification-code', data);
  return response.data;
};

/**
 * Auth-related API methods.
 */
export const authService = {
  signUpUser,
  sendVerificationCode,
};
