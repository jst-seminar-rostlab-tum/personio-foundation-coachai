'use client';

import { Button } from '@/components/ui/Button';
import { LayoutDashboard, RefreshCw, ServerCrash } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import '@/styles/globals.css';
import { useTranslations } from 'next-intl';

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  const router = useRouter();
  const t = useTranslations('Common.errorPage');

  useEffect(() => {
    console.error('Global error:', error);
  }, [error]);

  const handleTryAgain = () => {
    reset();
  };

  const handleBackDashboard = () => {
    router.push('/dashboard');
  };

  return (
    <html>
      <body>
        <div className="min-h-screen min-w-screen flex items-center justify-center py-4 px-4">
          <div className="w-full max-w-md text-center">
            <div className="flex flex-col items-center gap-6">
              <div className="w-16 h-16 bg-flame-10 rounded-full flex items-center justify-center">
                <ServerCrash className="w-8 h-8 text-flame-50" />
              </div>

              <div className="space-y-2">
                <h1 className="text-2xl font-bold text-bw-70">{t('title')}</h1>
              </div>

              <p className="text-bw-40 text-sm leading-relaxed max-w-sm">{t('description')}</p>

              <div className="flex md:flex-row flex-col gap-3 w-full max-w-xs justify-center">
                <Button onClick={handleTryAgain}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {t('tryAgain')}
                </Button>
                <Button onClick={handleBackDashboard} variant="outline">
                  <LayoutDashboard className="w-4 h-4 mr-2" />
                  {t('backDashboard')}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
