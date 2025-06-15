import { type NextRequest, NextResponse } from 'next/server';
import routing from '@/i18n/routing';
import { createClient } from './server';

const acceptedLocales = routing.locales
  .map(String)
  .concat(!!routing.localePrefix && routing.localePrefix === 'as-needed' ? [''] : []);

const stripLocaleFromPath = (path: string): string => {
  for (const locale of acceptedLocales) {
    const localePrefix = locale ? `/${locale}` : '';
    if (path === localePrefix || path.startsWith(`${localePrefix}/`)) {
      return path.slice(localePrefix.length) || '/';
    }
  }
  return path;
};

const publicRoutes = ['/', '/terms', '/privacy'];
const authRoutes = ['/login', '/confirm'];

export async function authMiddleware(
  request: NextRequest,
  response: NextResponse
): Promise<NextResponse> {
  const path = stripLocaleFromPath(request.nextUrl.pathname);
  const isAuthRoute = authRoutes.includes(path);
  const isPublicRoute = publicRoutes.includes(path);

  if (isPublicRoute) {
    return response;
  }

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) {
    if (isAuthRoute) {
      return response;
    }
    return NextResponse.redirect(new URL('/login', request.nextUrl));
  }

  if (isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.nextUrl));
  }

  return response;
}
