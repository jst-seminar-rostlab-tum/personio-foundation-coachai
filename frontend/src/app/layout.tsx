import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import type { LayoutProps } from '@/interfaces/LayoutProps';
import { headers } from 'next/headers';

export default async function RootLayout({ children, params }: LayoutProps) {
  const { locale } = await params;
  const nonce = (await headers()).get('x-nonce') || undefined;

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider>{children}</NextIntlClientProvider>
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
