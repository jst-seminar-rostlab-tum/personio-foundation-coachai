/**
 * Current node environment string.
 */
export const NODE_ENV = process.env.NODE_ENV || 'development';
/**
 * True when running in development mode.
 */
export const IS_DEVELOPMENT = NODE_ENV === 'development';
/**
 * True when running in production mode.
 */
export const IS_PRODUCTION = NODE_ENV === 'production';

/**
 * Supabase URL for client access.
 */
export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://127.0.0.1:54321';
/**
 * Supabase anonymous key for client access.
 */
export const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
/**
 * Base URL for the backend API.
 */
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Public base URL for the frontend.
 */
export const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';

/**
 * Enables skipping auth in development mode.
 */
export const DEV_MODE_SKIP_AUTH = process.env.NEXT_PUBLIC_DEV_MODE_SKIP_AUTH === 'true';
/**
 * Enables skipping email verification.
 */
export const SKIP_EMAIL_VERIFICATION = process.env.NEXT_PUBLIC_SKIP_EMAIL_VERIFICATION === 'true';
