export const NODE_ENV = process.env.NODE_ENV || 'development';
export const IS_DEVELOPMENT = NODE_ENV === 'development';
export const IS_PRODUCTION = NODE_ENV === 'production';

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://127.0.0.1:54321';
export const SUPABASE_ANON_KEY =
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0';

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const BASE_URL =
  process.env.NEXT_PUBLIC_BASE_URL || 'https://coachai-personio-foundation.vercel.app';

export const STAGING_URL = 'https://coachai-dev-personio-foundation.vercel.app';

export const DEV_MODE_SKIP_AUTH = process.env.NEXT_PUBLIC_DEV_MODE_SKIP_AUTH === 'true';

export const config = {
  env: {
    NODE_ENV,
    IS_DEVELOPMENT,
    IS_PRODUCTION,
  },
  supabase: {
    url: SUPABASE_URL,
    anonKey: SUPABASE_ANON_KEY,
  },
  api: {
    url: API_URL,
  },
  app: {
    baseUrl: BASE_URL,
  },
  development: {
    skipAuth: DEV_MODE_SKIP_AUTH,
  },
} as const;

export default config;
