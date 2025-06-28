import { CreateUserRequest } from '@/interfaces/models/Auth';
import { createClient } from '@/lib/supabase/client';
import { redirect } from 'next/navigation';
import { api } from './Api';

const createUser = async (data: CreateUserRequest) => {
  const response = await api.post('/auth', data);
  return response.data;
};

const confirmUser = async () => {
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
