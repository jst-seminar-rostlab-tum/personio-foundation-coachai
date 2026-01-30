import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { Inter, Bebas_Neue as BebasNeue } from 'next/font/google';
import type { Viewport } from 'next';

import { getLocale } from 'next-intl/server';
import { headers } from 'next/headers';
import Script from 'next/script';
import { BASE_URL } from '@/lib/connector';

const inter = Inter({ subsets: ['latin'] });
const bebasNeue = BebasNeue({ subsets: ['latin'], weight: '400' });

/**
 * Global viewport configuration for the app.
 */
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

/**
 * Props for the root layout.
 */
interface RootLayoutProps {
  children: React.ReactNode;
}

/**
 * Provides the root HTML structure, fonts, and JSON-LD schema.
 */
export default async function RootLayout({ children }: RootLayoutProps) {
  const locale = await getLocale();
  const nonce = (await headers()).get('x-nonce') || '';

  /**
   * JSON-LD metadata for search engines.
   */
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'Coach AI',
    url: BASE_URL,
  };

  return (
    <html lang={locale} className={bebasNeue.className}>
      <head>
        <Script
          id="jsonld-root"
          type="application/ld+json"
          nonce={nonce}
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className={inter.className}>
        <NextIntlClientProvider>{children}</NextIntlClientProvider>
      </body>
    </html>
  );
}

export const dynamic = 'force-dynamic';
