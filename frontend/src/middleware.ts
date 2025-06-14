import createMiddleware from 'next-intl/middleware';
import { NextRequest } from 'next/server';
import { authMiddleware } from '@/lib/supabase/middleware';
import routing from '@/i18n/routing';

const i18nMiddleware = createMiddleware(routing);

export default async function middleware(request: NextRequest) {
  const response = i18nMiddleware(request);

  // Skip authentication if in development mode and the environment variable is set
  if (process.env.NODE_ENV === 'development') {
    return response;
  }

  return authMiddleware(request, response);
}

export const config = {
  // Match all pathnames except for
  // - … if they start with `/api`, `/trpc`, `/_next` or `/_vercel`
  // - … the ones containing a dot (e.g. `favicon.ico`)
  matcher: '/((?!api|trpc|_next|_vercel|.*\\..*).*)',
};
