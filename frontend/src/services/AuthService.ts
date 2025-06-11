import { CreateUserRequest } from '@/interfaces/auth/CreateUserRequest';
import { api } from './Api';

const createUser = async (data: CreateUserRequest) => {
  const response = await api.post('/auth/', data);
  return response.data;
};

export const authService = {
  createUser,
};
