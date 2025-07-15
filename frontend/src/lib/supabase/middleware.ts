import { type NextRequest, NextResponse } from 'next/server';
import routing from '@/i18n/routing';
import { jwtDecode } from 'jwt-decode';
import { AccountRole } from '@/interfaces/models/UserProfile';
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
const authRoutes = ['/login'];
const adminRoutes = ['/admin'];

export async function authMiddleware(
  request: NextRequest,
  response: NextResponse
): Promise<NextResponse> {
  const path = stripLocaleFromPath(request.nextUrl.pathname);
  const isAuthRoute = authRoutes.includes(path);
  const isPublicRoute = publicRoutes.includes(path);
  const isAdminRoute = adminRoutes.includes(path);

  if (isPublicRoute) {
    return response;
  }

  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  const user = session?.user;

  if (!user) {
    if (isAuthRoute) return response;
    return NextResponse.redirect(new URL('/login', request.nextUrl));
  }

  if (isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.nextUrl));
  }

  if (isAdminRoute) {
    const accessToken = session?.access_token;

    if (!accessToken) {
      console.warn('Missing access token for admin route');
      return NextResponse.redirect(new URL('/dashboard', request.nextUrl));
    }

    try {
      const decoded = jwtDecode<{ account_role?: string }>(accessToken);
      const role = decoded.account_role;

      if (!role || role !== AccountRole.admin) {
        console.warn(`User is not admin: role=${role}`);
        return NextResponse.redirect(new URL('/dashboard', request.nextUrl));
      }
    } catch (err) {
      console.error('JWT decode error:', err);
      return NextResponse.redirect(new URL('/dashboard', request.nextUrl));
    }
  }

  return response;
}
