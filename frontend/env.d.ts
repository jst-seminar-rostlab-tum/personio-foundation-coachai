declare namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_SUPABASE_URL: string;
    NEXT_PUBLIC_SUPABASE_ANON_KEY: string;
    NEXT_PUBLIC_DEV_MODE_SKIP_AUTH: string;
    NEXT_PUBLIC_SKIP_EMAIL_VERIFICATION: string;
    NEXT_PUBLIC_API_URL: string; // defaults to http://localhost:8000
    NEXT_PUBLIC_BASE_URL: string; // defaults to https://coachai-personio-foundation.vercel.app
    NEXT_PUBLIC_SENTRY_DSN: string;
  }
}
