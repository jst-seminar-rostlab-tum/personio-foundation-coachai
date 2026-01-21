import { UserCreate, VerificationCodeCreate } from '@/interfaces/models/Auth';
import { AxiosInstance } from 'axios';

const signUpUser = async (api: AxiosInstance, data: UserCreate) => {
  const response = await api.post('/auth/sign-up-user', data);
  return response.data;
};

const sendVerificationCode = async (api: AxiosInstance, data: VerificationCodeCreate) => {
  const response = await api.post('/auth/send-phone-verification-code', data);
  return response.data;
};

export const authService = {
  signUpUser,
  sendVerificationCode,
};
