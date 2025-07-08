import createMiddleware from 'next-intl/middleware';
import { NextRequest, NextResponse } from 'next/server';
import { authMiddleware } from '@/lib/supabase/middleware';
import routing from '@/i18n/routing';

const allowedOrigins = [
  'https://coachai-personio-foundation.vercel.app',
  'https://coachai-dev-personio-foundation.vercel.app',
  'http://localhost:3000',
];

const corsHeaders = {
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

const i18nMiddleware = createMiddleware(routing);

export default async function middleware(request: NextRequest) {
  const origin = request.headers.get('origin') || '';
  const isAllowedOrigin = allowedOrigins.includes(origin);
  const isPreflight = request.method === 'OPTIONS';

  if (isPreflight && isAllowedOrigin) {
    return NextResponse.json(
      {},
      {
        headers: {
          ...corsHeaders,
          'Access-Control-Allow-Origin': origin,
        },
      }
    );
  }

  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
  const isDev = process.env.NODE_ENV !== 'production';
  const cspHeader = `
    default-src 'self';
    connect-src 'self' ${process.env.NEXT_PUBLIC_SUPABASE_URL} ${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'} https://api.openai.com;
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic' ${isDev ? 'unsafe-eval' : ''};
    style-src 'self' 'unsafe-inline';
    img-src 'self' blob: data:;
    frame-src 'self' https://vercel.live;
    media-src 'self' https://storage.googleapis.com;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
`;
  const contentSecurityPolicyHeaderValue = cspHeader.replace(/\s{2,}/g, ' ').trim();

  const response = i18nMiddleware(request);
  response.headers.set('x-nonce', nonce);
  response.headers.set('Content-Security-Policy', contentSecurityPolicyHeaderValue);
  if (isAllowedOrigin) {
    response.headers.set('Access-Control-Allow-Origin', origin);
  }

  Object.entries(corsHeaders).forEach(([key, value]) => {
    response.headers.set(key, value);
  });
  if (
    process.env.NODE_ENV === 'development' &&
    process.env.NEXT_PUBLIC_DEV_MODE_SKIP_AUTH === 'true'
  ) {
    return response;
  }
  return authMiddleware(request, response);
}

export const config = {
  matcher: '/((?!api|_next|_vercel|.*\\.[^/]+$).*)',
};
