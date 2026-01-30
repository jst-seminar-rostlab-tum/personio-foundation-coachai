import axios from 'axios';
import { createClient } from '@/lib/supabase/server';
import { API_URL } from '@/lib/connector';
import { setupAuthInterceptor } from './AuthInterceptor';

/**
 * Axios client configured for server-side API calls.
 */
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Attaches auth interceptor to the server API client.
 */
setupAuthInterceptor(api, createClient);
