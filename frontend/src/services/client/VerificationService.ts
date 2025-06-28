import { SendVerificationCodeRequest, VerifyCodeRequest } from '@/interfaces/models/Auth';
import { api } from './Api';

const sendVerificationCode = async (data: SendVerificationCodeRequest) => {
  const response = await api.post('/auth/send-verification', data);
  return response.data;
};

const verifyCode = async (data: VerifyCodeRequest) => {
  const response = await api.post('/auth/verify-code', data);
  return response.data;
};

export const verificationService = {
  sendVerificationCode,
  verifyCode,
};
