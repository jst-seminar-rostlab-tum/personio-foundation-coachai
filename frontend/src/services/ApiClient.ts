import axios from 'axios';
import { createClient } from '@/lib/supabase/client';
import { API_URL } from '@/lib/connector';
import { setupAuthInterceptor } from './AuthInterceptor';

export const api = axios.create({
  baseURL: API_URL,
});

setupAuthInterceptor(api, createClient);
