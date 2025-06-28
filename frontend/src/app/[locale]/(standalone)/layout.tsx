import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { LayoutProps } from '@/interfaces/LayoutProps';
import { Toaster } from '@/components/ui/Sonner';
import { headers } from 'next/headers';

const inter = Inter({ subsets: ['latin'] });

export default async function StandaloneLayout({ children, params }: LayoutProps) {
  const { locale } = await params;
  const nonce = (await headers()).get('x-nonce') || undefined;

  return (
    <html lang={locale}>
      <body className={inter.className}>
        <main className="w-full">
          <NextIntlClientProvider>{children}</NextIntlClientProvider>
        </main>
        <Toaster richColors />
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
