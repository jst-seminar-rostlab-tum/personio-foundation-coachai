import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import AboutHeader from '@/components/layout/AboutHeader';
import AboutFooter from '@/components/layout/AboutFooter';
import type { LayoutProps } from '@/interfaces/props/LayoutProps';
import { Toaster } from '@/components/ui/Sonner';

export default async function AuthLayout({ children }: LayoutProps) {
  return (
    <NextIntlClientProvider>
      <AboutHeader />
      <main className="container mx-auto px-4">{children}</main>
      <Toaster richColors />
      <AboutFooter />
    </NextIntlClientProvider>
  );
}

export const dynamic = 'force-dynamic';
