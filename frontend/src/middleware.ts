import createMiddleware from 'next-intl/middleware';
import { NextRequest } from 'next/server';
import { authMiddleware } from '@/lib/supabase/middleware';
import routing from '@/i18n/routing';

const i18nMiddleware = createMiddleware(routing);

export default async function middleware(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
  const cspHeader = `
    default-src 'self';
    connect-src 'self' ${process.env.NODE_ENV === 'production' ? '' : `${process.env.NEXT_PUBLIC_API_URL}`};
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic' ${process.env.NODE_ENV === 'production' ? '' : `'unsafe-eval'`};
    style-src 'self' 'unsafe-inline';
    img-src 'self' blob: data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    upgrade-insecure-requests;
`;
  // Replace newline characters and spaces
  const contentSecurityPolicyHeaderValue = cspHeader.replace(/\s{2,}/g, ' ').trim();

  const response = i18nMiddleware(request);

  response.headers.set('x-nonce', nonce);
  response.headers.set('Content-Security-Policy', contentSecurityPolicyHeaderValue);

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
  // - … the ones containing a dot (e.g. `favicon.ico`)
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    {
      source: '/((?!api|_next|_vercel|.*\\.[^/]+$).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
};
