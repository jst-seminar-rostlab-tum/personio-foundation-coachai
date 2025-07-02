import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import AboutHeader from '@/components/layout/AboutHeader';
import AboutFooter from '@/components/layout/AboutFooter';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';

import type { LayoutProps } from '@/interfaces/props/LayoutProps';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { headers } from 'next/headers';

const inter = Inter({ subsets: ['latin'] });

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;

  return generateDynamicMetadata(locale, '', false);
}

export default async function RootLayout({ children, params }: LayoutProps) {
  const { locale } = await params;
  const nonce = (await headers()).get('x-nonce') || undefined;
  return (
    <html lang={locale}>
      <body className={inter.className}>
        <NextIntlClientProvider>
          <AboutHeader />
          <main className="container mx-auto p-6 md:p-12 mt-16">{children}</main>
          <AboutFooter />
        </NextIntlClientProvider>
        <script
          nonce={nonce}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'WebSite',
              name: 'Coach AI',
              url: 'https://personiofoundation-coachai.com',
            }),
          }}
        />
      </body>
    </html>
  );
}

export const dynamic = 'force-dynamic';
