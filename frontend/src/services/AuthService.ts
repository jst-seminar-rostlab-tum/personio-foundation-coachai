import {
  CreateUserRequest,
  SendVerificationCodeRequest,
  VerifyCodeRequest,
} from '@/interfaces/models/Auth';
import { AxiosInstance } from 'axios';

const createUser = async (api: AxiosInstance, data: CreateUserRequest) => {
  const response = await api.post('/auth', data);
  return response.data;
};

const confirmUser = async (api: AxiosInstance) => {
  const response = await api.get('/auth/confirm');
  return response.data;
};

const sendVerificationCode = async (api: AxiosInstance, data: SendVerificationCodeRequest) => {
  const response = await api.post('/auth/send-verification', data);
  return response.data;
};

const verifyCode = async (api: AxiosInstance, data: VerifyCodeRequest) => {
  const response = await api.post('/auth/verify-code', data);
  return response.data;
};

export const authService = {
  createUser,
  confirmUser,
  sendVerificationCode,
  verifyCode,
};
