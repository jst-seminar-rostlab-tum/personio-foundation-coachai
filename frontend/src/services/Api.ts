import { SignInCredentials, UserProfileCreate } from '@/interfaces/Api';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers?.set?.('Authorization', `Bearer ${token}`);
    }
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

export const userProfileApi = {
  create: async (data: UserProfileCreate) => {
    const response = await api.post('/user-profiles/', data);
    return response.data;
  },
  validate: async (data: UserProfileCreate) => {
    const response = await api.post('/user-profiles/validate', data);
    return response.data;
  },
  signIn: async (credentials: SignInCredentials) => {
    const response = await api.post('/user-profiles/sign-in', credentials);
    return response.data;
  },
};

export default api;
