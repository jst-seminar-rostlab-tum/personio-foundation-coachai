import { CreateUserRequest } from '@/interfaces/auth/CreateUserRequest';
import { apiService } from './api.service';

export const authService = {
  create: async (data: CreateUserRequest) => {
    const response = await apiService.post('/auth/', data);
    return response.data;
  },
};
