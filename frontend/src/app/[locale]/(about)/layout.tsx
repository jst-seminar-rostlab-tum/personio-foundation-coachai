import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import AboutHeader from '@/components/layout/AboutHeader';
import AboutFooter from '@/components/layout/AboutFooter';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Props } from '@/interfaces/LayoutProps';

const inter = Inter({ subsets: ['latin'] });

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '', false);
}

export default async function RootLayout({ children, params }: Props) {
  const { locale } = await params;

  return (
    <html lang={locale}>
      <head>
        <script
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
      </head>
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
