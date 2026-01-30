import createMiddleware from 'next-intl/middleware';
import { NextRequest, NextResponse } from 'next/server';
import { authMiddleware } from '@/lib/supabase/middleware';
import routing from '@/i18n/routing';
import {
  API_URL,
  BASE_URL,
  DEV_MODE_SKIP_AUTH,
  IS_DEVELOPMENT,
  SUPABASE_URL,
} from './lib/connector';

/**
 * Allowed origins for CORS responses.
 */
const allowedOrigins = [BASE_URL];

/**
 * CORS headers applied to responses.
 */
const corsHeaders = {
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

/**
 * Locale-aware middleware from next-intl.
 */
const i18nMiddleware = createMiddleware(routing);

/**
 * Applies i18n routing, CSP headers, CORS handling, and auth protection.
 */
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

  /**
   * Content Security Policy with a per-request nonce.
   */
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
  const cspHeader = `
    default-src 'self';
    connect-src 'self' ${SUPABASE_URL} ${API_URL} https://api.openai.com;
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic' ${IS_DEVELOPMENT ? 'unsafe-eval' : ''};
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
  if (IS_DEVELOPMENT && DEV_MODE_SKIP_AUTH) {
    return response;
  }
  return authMiddleware(request, response);
}

export const config = {
  matcher: '/((?!api|_next|_vercel|.*\\.[^/]+$).*)',
};
