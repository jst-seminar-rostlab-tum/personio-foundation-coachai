import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import AboutHeader from '@/components/layout/AboutHeader';
import AboutFooter from '@/components/layout/AboutFooter';
import type { LayoutProps } from '@/interfaces/props/LayoutProps';
import { Toaster } from '@/components/ui/Sonner';

/**
 * Provides the shared layout chrome for auth pages with header, footer, and toasts.
 */
export default async function AuthLayout({ children }: LayoutProps) {
  return (
    <NextIntlClientProvider>
      <AboutHeader />
      <main className="mx-auto px-[clamp(1.25rem,4vw,4rem)] max-w-7xl">{children}</main>
      <Toaster richColors />
      <AboutFooter />
    </NextIntlClientProvider>
  );
}

export const dynamic = 'force-dynamic';
