import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import AboutHeader from '@/components/layout/AboutHeader';
import AboutFooter from '@/components/layout/AboutFooter';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { LayoutProps } from '@/interfaces/props/LayoutProps';
import { MetadataProps } from '@/interfaces/props/MetadataProps';

const inter = Inter({ subsets: ['latin'] });

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '', false);
}

export default async function RootLayout({ children, params }: LayoutProps) {
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
        <NextIntlClientProvider>
          <AboutHeader />
          <main className="mx-auto py-12 px-[clamp(1.25rem,4vw,4rem)] max-w-7xl mt-16">
            {children}
          </main>
          <AboutFooter />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
