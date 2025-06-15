import { CreateUserRequest } from '@/interfaces/auth/CreateUserRequest';
import { createClient } from '@/lib/supabase/client';
import { AxiosInstance } from 'axios';
import { redirect } from 'next/navigation';

const createUser = async (api: AxiosInstance, data: CreateUserRequest) => {
  const response = await api.post('/auth/', data);
  return response.data;
};

const confirmUser = async (api: AxiosInstance) => {
  const response = await api.get('/auth/confirm');
  return response.data;
};

const logoutUser = async () => {
  const supabase = await createClient();
  const { error } = await supabase.auth.signOut();
  if (error) {
    console.error('Error signing out:', error);
  }

  redirect('/');
};

export const authService = {
  createUser,
  confirmUser,
  logoutUser,
};
