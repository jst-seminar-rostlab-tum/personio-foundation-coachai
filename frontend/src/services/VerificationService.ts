import { SendVerificationCodeRequest, VerifyCodeRequest } from '@/interfaces/models/Auth';
import { AxiosInstance } from 'axios';

const sendVerificationCode = async (api: AxiosInstance, data: SendVerificationCodeRequest) => {
  const response = await api.post('/auth/send-verification', data);
  return response.data;
};

const verifyCode = async (api: AxiosInstance, data: VerifyCodeRequest) => {
  const response = await api.post('/auth/verify-code', data);
  return response.data;
};

export const verificationService = {
  sendVerificationCode,
  verifyCode,
};
