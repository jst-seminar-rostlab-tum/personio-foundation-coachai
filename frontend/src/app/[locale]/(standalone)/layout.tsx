import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { LayoutProps } from '@/interfaces/LayoutProps';
import { Toaster } from '@/components/ui/Sonner';
import Head from 'next/head';

const inter = Inter({ subsets: ['latin'] });

export default async function StandaloneLayout({ children, params }: LayoutProps) {
  const { locale } = await params;

  return (
    <>
      <Head>
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
      </Head>
      <div className={inter.className}>
        <NextIntlClientProvider locale={locale}>
          <main className="w-full">{children}</main>
          <Toaster richColors />
        </NextIntlClientProvider>
      </div>
    </>
  );
}
