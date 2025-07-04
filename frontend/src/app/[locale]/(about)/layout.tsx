import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import AboutHeader from '@/components/layout/AboutHeader';
import AboutFooter from '@/components/layout/AboutFooter';
import type { LayoutProps } from '@/interfaces/props/LayoutProps';

export default async function AboutLayout({ children }: LayoutProps) {
  return (
    <NextIntlClientProvider>
      <AboutHeader />
      <main className="mx-auto py-8 px-[clamp(1.25rem,4vw,4rem)] max-w-7xl">{children}</main>
      <AboutFooter />
    </NextIntlClientProvider>
  );
}

export const dynamic = 'force-dynamic';
