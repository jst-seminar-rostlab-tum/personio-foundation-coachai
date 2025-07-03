import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import AboutHeader from '@/components/layout/AboutHeader';
import AboutFooter from '@/components/layout/AboutFooter';
import type { LayoutProps } from '@/interfaces/props/LayoutProps';

export default async function AboutLayout({ children }: LayoutProps) {
  return (
    <NextIntlClientProvider>
      <AboutHeader />
      <main className="container mx-auto p-6 md:p-12 mt-16">{children}</main>
      <AboutFooter />
    </NextIntlClientProvider>
  );
}

export const dynamic = 'force-dynamic';
