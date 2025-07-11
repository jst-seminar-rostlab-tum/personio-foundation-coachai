import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { LayoutProps } from '@/interfaces/props/LayoutProps';
import { AppHeader } from '@/components/layout/AppHeader';
import BackButton from '@/components/common/BackButton';
import { Toaster } from '@/components/ui/Sonner';
import { UserContextProvider } from '@/contexts/User';

export default async function MainLayout({ children }: LayoutProps) {
  return (
    <NextIntlClientProvider>
      <UserContextProvider>
        <AppHeader />
        <main className="mx-auto py-12 px-[clamp(1.25rem,4vw,4rem)] max-w-7xl mt-16">
          <BackButton />
          {children}
        </main>
        <Toaster richColors />
      </UserContextProvider>
    </NextIntlClientProvider>
  );
}

export const dynamic = 'force-dynamic';
