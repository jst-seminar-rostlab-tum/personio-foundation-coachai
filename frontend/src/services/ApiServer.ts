import axios from 'axios';
import { createClient } from '@/lib/supabase/server';
import { API_URL } from '@/lib/connector';
import { setupAuthInterceptor } from './AuthInterceptor';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

setupAuthInterceptor(api, createClient);
