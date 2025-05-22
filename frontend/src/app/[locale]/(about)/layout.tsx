import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import AboutHeader from '@/components/layout/AboutHeader';
import AboutFooter from '@/components/layout/AboutFooter';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Next.js + FastAPI App',
  description: 'Web application built with Next.js and FastAPI',
  manifest: '/manifest.json',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AboutHeader />
        <main className="container mx-auto px-4">
          <NextIntlClientProvider>{children}</NextIntlClientProvider>
        </main>
        <AboutFooter />
      </body>
    </html>
  );
}
