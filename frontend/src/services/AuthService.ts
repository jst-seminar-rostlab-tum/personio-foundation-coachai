import { CreateUserRequest } from '@/interfaces/auth/CreateUserRequest';
import { api } from './Api';

const createUser = async (data: CreateUserRequest) => {
  const response = await api.post('/auth/', data);
  return response.data;
};

const confirmUser = async () => {
  const response = await api.get('/auth/confirm');
  return response.data;
};

export const authService = {
  createUser,
  confirmUser,
};
