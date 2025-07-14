import '@/styles/globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { LayoutProps } from '@/interfaces/props/LayoutProps';
import { Toaster } from '@/components/ui/Sonner';

export default async function StandaloneLayout({ children }: LayoutProps) {
  return (
    <NextIntlClientProvider>
      <main className="w-full">{children}</main>
      <Toaster richColors />
    </NextIntlClientProvider>
  );
}

export const dynamic = 'force-dynamic';
