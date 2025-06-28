import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import AboutHeader from '@/components/layout/AboutHeader';
import AboutFooter from '@/components/layout/AboutFooter';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { LayoutProps } from '@/interfaces/LayoutProps';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { Toaster } from '@/components/ui/Sonner';
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
          <main className="container mx-auto px-4">{children}</main>
          <Toaster richColors />
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
