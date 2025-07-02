import { Inter, Bebas_Neue as BebasNeue } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { LayoutProps } from '@/interfaces/props/LayoutProps';
import { AppHeader } from '@/components/layout/AppHeader';
import BackButton from '@/components/common/BackButton';
import { Toaster } from '@/components/ui/Sonner';

import { UserContextProvider } from '@/contexts/User';
import { UserProfileService } from '@/services/UserProfileService';
import { api } from '@/services/ApiServer';
import { headers } from 'next/headers';

const inter = Inter({ subsets: ['latin'] });
const bebasNeue = BebasNeue({ subsets: ['latin'], weight: '400' });

export default async function RootLayout({ children, params }: LayoutProps) {
  const { locale } = await params;

  const userProfile = await UserProfileService.getUserProfile(api);
  const nonce = (await headers()).get('x-nonce') || undefined;

  return (
    <html lang={locale} className={bebasNeue.className}>
      <body className={inter.className}>
        <NextIntlClientProvider>
          <UserContextProvider user={userProfile}>
            <AppHeader />
            <main className="mx-auto py-12 px-[clamp(1.25rem,4vw,4rem)] max-w-7xl mt-16">
              <BackButton />
              {children}
            </main>
            <Toaster richColors />
          </UserContextProvider>
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
