import { createClient } from '@/lib/supabase/server';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  async (config) => {
    if (config.url?.includes('/auth') && !config.url?.includes('/auth/confirm')) {
      return config;
    }

    if (process.env.NODE_ENV === 'development') {
      return config;
    }

    const supabase = await createClient();
    const { data, error } = await supabase.auth.getSession();
    if (error || !data.session) {
      return Promise.reject(error);
    }
    const accessToken = data.session.access_token;
    config.headers.set('Authorization', `Bearer ${accessToken}`);

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error;
    console.warn(response);
    // Handle different error statuses here if needed
    return Promise.reject(error);
  }
);
