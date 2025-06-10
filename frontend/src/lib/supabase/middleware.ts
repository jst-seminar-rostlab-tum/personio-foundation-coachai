import { createServerClient } from '@supabase/ssr';
import { type NextRequest, NextResponse } from 'next/server';
import routing from '@/i18n/routing';

const acceptedLocales = routing.locales
  .map(String)
  .concat(!!routing.localePrefix && routing.localePrefix === 'as-needed' ? [''] : []);

const getLocalizedPaths = (urls: string[]): string[] => {
  return acceptedLocales.flatMap((locale) =>
    urls.map((url) => `/${locale}/${url}`.replace(/\/+/g, '/'))
  );
};

export async function authMiddleware(
  request: NextRequest,
  response: NextResponse
): Promise<NextResponse> {
  const { pathname } = request.nextUrl;

  const publicUrls = ['/terms', '/privacy'];
  if (
    acceptedLocales.some((locale) => pathname === `/${locale}`) ||
    getLocalizedPaths(publicUrls).some((path) => pathname.startsWith(path))
  ) {
    return response;
  }

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const authUrls = ['/login', '/confirm'];
  if (!user) {
    if (getLocalizedPaths(authUrls).some((path) => pathname.startsWith(path))) {
      return response;
    }

    const url = request.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }

  if (getLocalizedPaths(authUrls).some((path) => pathname.startsWith(path))) {
    const url = request.nextUrl.clone();
    url.pathname = '/dashboard';
    url.search = '';
    url.hash = '';
    return NextResponse.redirect(url);
  }

  return response;
}
