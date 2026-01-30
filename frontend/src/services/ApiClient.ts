import axios from 'axios';
import { createClient } from '@/lib/supabase/client';
import { API_URL } from '@/lib/connector';
import { setupAuthInterceptor } from './AuthInterceptor';

/**
 * Axios client configured for browser API calls.
 */
export const api = axios.create({
  baseURL: API_URL,
});

/**
 * Attaches auth interceptor to the API client.
 */
setupAuthInterceptor(api, createClient);
