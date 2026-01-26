import { createClient } from '@/lib/supabase/server';
import { NextRequest, NextResponse } from 'next/server';

/**
 * Handles email change redirects and refreshes the Supabase session.
 */
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  if (searchParams.has('error')) {
    return NextResponse.redirect(new URL('', req.nextUrl.origin));
  }

  const supabase = await createClient();
  try {
    await supabase.auth.refreshSession();
  } catch {
    return NextResponse.redirect(new URL(`/`, req.nextUrl.origin));
  }

  return NextResponse.redirect(
    new URL('/settings?emailUpdatedSuccess=email_changed', req.nextUrl.origin)
  );
}
