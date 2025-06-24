import { Inter, Bebas_Neue as BebasNeue } from 'next/font/google';
import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { LayoutProps } from '@/interfaces/LayoutProps';
import { AppHeader } from '@/components/layout/AppHeader';
import BackButton from '@/components/common/BackButton';
import { Toaster } from '@/components/ui/Sonner';
import { UserContextProvider } from '@/lib/context/user';
import { UserProfileService } from '@/services/server/UserProfileService';
import Head from 'next/head';

const inter = Inter({ subsets: ['latin'] });
const bebasNeue = BebasNeue({ subsets: ['latin'], weight: '400' });

export default async function RootLayout({ children, params }: LayoutProps) {
  const { locale } = await params;
  const userProfile = await UserProfileService.getUserProfile();

  return (
    <div lang={locale} className={bebasNeue.className}>
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

      <NextIntlClientProvider locale={locale}>
        <UserContextProvider user={userProfile}>
          <div className={inter.className}>
            <AppHeader />
            <main className="container mx-auto p-6 md:p-12 mt-16">
              <BackButton />
              {children}
            </main>
            <Toaster richColors />
          </div>
        </UserContextProvider>
      </NextIntlClientProvider>
    </div>
  );
}
