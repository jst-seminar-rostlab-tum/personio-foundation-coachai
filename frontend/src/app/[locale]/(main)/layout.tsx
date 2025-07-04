import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { LayoutProps } from '@/interfaces/props/LayoutProps';
import { AppHeader } from '@/components/layout/AppHeader';
import BackButton from '@/components/common/BackButton';
import { Toaster } from '@/components/ui/Sonner';

import { UserContextProvider } from '@/contexts/User';
import { UserProfileService } from '@/services/UserProfileService';
import { api } from '@/services/ApiServer';

export default async function MainLayout({ children }: LayoutProps) {
  const userProfile = await UserProfileService.getUserProfile(api);

  return (
    <NextIntlClientProvider>
      <UserContextProvider user={userProfile}>
        <AppHeader />
        <main className="container mx-auto p-6 md:p-12 mt-16">
          <BackButton />
          {children}
        </main>
        <Toaster richColors />
      </UserContextProvider>
    </NextIntlClientProvider>
  );
}

export const dynamic = 'force-dynamic';
