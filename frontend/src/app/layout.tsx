import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import type { LayoutProps } from '@/interfaces/LayoutProps';

export default async function RootLayout({ children, params }: LayoutProps) {
  const { locale } = await params;

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider>{children}</NextIntlClientProvider>
      </body>
    </html>
  );
}
