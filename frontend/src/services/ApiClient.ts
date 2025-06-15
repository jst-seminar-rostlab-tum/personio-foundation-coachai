import axios from 'axios';
import { createClient } from '@/lib/supabase/client';
import { setupAuthInterceptor } from './Interceptor';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

setupAuthInterceptor(api, createClient);
