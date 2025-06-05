import { createClient } from '@/utils/supabase/client';
import axios from 'axios';

const supabase = createClient();

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  async (config) => {
    const { data, error } = await supabase.auth.getSession();
    if (error || !data.session) {
      return Promise.reject(error);
    }

    // Check if the session is expired and refresh it if necessary
    let accessToken = data.session.access_token;
    const currentTime = Math.floor(Date.now() / 1000);
    const sessionExpiry = data.session.expires_at;
    if (!sessionExpiry || sessionExpiry < currentTime) {
      const { data: refreshedData, error: refreshError } = await supabase.auth.refreshSession();
      if (refreshError || !refreshedData.session) {
        return Promise.reject(refreshError || new Error('Session refresh failed'));
      }
      accessToken = refreshedData.session.access_token;
    }

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

export default api;
