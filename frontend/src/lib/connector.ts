export const NODE_ENV = process.env.NODE_ENV || 'development';
export const IS_DEVELOPMENT = NODE_ENV === 'development';
export const IS_PRODUCTION = NODE_ENV === 'production';

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://127.0.0.1:54321';
export const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';

export const DEV_MODE_SKIP_AUTH = process.env.NEXT_PUBLIC_DEV_MODE_SKIP_AUTH === 'true';
export const SKIP_EMAIL_VERIFICATION = process.env.NEXT_PUBLIC_SKIP_EMAIL_VERIFICATION === 'true';
