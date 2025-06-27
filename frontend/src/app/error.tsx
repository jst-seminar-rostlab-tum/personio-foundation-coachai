'use client';

import { Button } from '@/components/ui/Button';
import { Home, RefreshCw, ServerCrash } from 'lucide-react';
import { useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { ErrorPageProps } from '@/interfaces/ErrorPageProps';

export default function Error({ error, reset }: ErrorPageProps) {
  const t = useTranslations('Common');

  useEffect(() => {
    console.error(error);
  }, [error]);

  const handleTryAgain = () => {
    reset();
  };

  return (
    <div className="min-h-screen min-w-screen flex items-center justify-center py-4 px-4">
      <div className="w-full max-w-md text-center">
        <div className="flex flex-col items-center gap-6">
          <div className="w-16 h-16 bg-flame-10 rounded-full flex items-center justify-center">
            <ServerCrash className="w-8 h-8 text-flame-50" />
          </div>

          <div className="space-y-2">
            <h1 className="text-2xl font-bold text-bw-70">{t('errorPage.title')}</h1>
          </div>

          <p className="text-bw-40 text-sm leading-relaxed max-w-sm">
            {t('errorPage.description')}
          </p>

          <div className="flex md:flex-row flex-col gap-3 w-full max-w-xs justify-center">
            <Button onClick={handleTryAgain}>
              <RefreshCw className="w-4 h-4 mr-2" />
              {t('tryAgain')}
            </Button>
            <Button asChild variant="outline">
              <Link href="/dashboard">
                <Home className="w-4 h-4 mr-2" />
                {t('backToHome')}
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
