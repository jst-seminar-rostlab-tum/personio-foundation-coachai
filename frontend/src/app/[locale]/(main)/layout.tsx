import { Inter, Barlow_Condensed as BarlowCondensed } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { Props } from '@/interfaces/LayoutProps';
import { AppHeader } from '@/components/layout/AppHeader';

const inter = Inter({ subsets: ['latin'] });

const barlowCondensed = BarlowCondensed({
  subsets: ['latin'],
  weight: ['500'],
  display: 'swap',
});

export default async function RootLayout({ children, params }: Props) {
  const { locale } = await params;

  return (
    <html lang={locale} className={barlowCondensed.className}>
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
          <AppHeader />
          <main className="container mx-auto p-4 mt-[56px]">{children}</main>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
