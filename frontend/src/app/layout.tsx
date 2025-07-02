import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { Inter, Bebas_Neue as BebasNeue } from 'next/font/google';

import type { LayoutProps } from '@/interfaces/props/LayoutProps';
import { headers } from 'next/headers';
import Script from 'next/script';

const inter = Inter({ subsets: ['latin'] });
const bebasNeue = BebasNeue({ subsets: ['latin'], weight: '400' });

export default async function RootLayout({ children, params }: LayoutProps) {
  const { locale } = await params;
  const nonce = (await headers()).get('x-nonce') || undefined;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'Coach AI',
    url: 'https://personiofoundation-coachai.com',
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
