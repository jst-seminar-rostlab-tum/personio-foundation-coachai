import { createServerClient } from '@supabase/ssr';
import { type NextRequest, NextResponse } from 'next/server';

export async function updateSession(
  request: NextRequest,
  response: NextResponse
): Promise<NextResponse> {
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
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true,
      },
    }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    if (request.nextUrl.pathname.startsWith('/confirm')) {
      return response;
    }

    if (!request.nextUrl.pathname.startsWith('/login')) {
      const url = request.nextUrl.clone();
      url.pathname = '/login';
      return NextResponse.redirect(url);
    }
  }

  const authUrls = ['/login', '/confirm'];
  if (user && authUrls.some((path) => request.nextUrl.pathname.startsWith(path))) {
    const url = request.nextUrl.clone();
    if (request.nextUrl.pathname.startsWith('/login')) {
      // Keep the current path and search params for /login
      return NextResponse.redirect(url);
    }

    // Redirect to home page, do not keep search params, etc.
    url.pathname = '/';
    url.search = '';
    url.hash = '';
    return NextResponse.redirect(url);
  }

  return response;
}
