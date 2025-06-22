'use client';

import { Button } from '@/components/ui/Button';
import { LayoutDashboard, RefreshCw, ServerCrash } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useTranslations } from 'next-intl';

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  const router = useRouter();
  const t = useTranslations('Common');

  useEffect(() => {
    console.error('Global error:', error);
  }, [error]);

  const handleTryAgain = () => {
    reset();
  };

  const handleBackAbout = () => {
    router.push('/');
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
                <h1 className="text-2xl font-bold text-bw-70">{t('errorPage.title')}</h1>
              </div>

              <p className="text-bw-40 text-sm leading-relaxed max-w-sm">
                {t('errorPage.description')}
              </p>

              <div className="flex md:flex-row flex-col gap-3 w-full max-w-xs justify-center">
                <Button onClick={handleTryAgain}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {t('errorPage.tryAgain')}
                </Button>
                <Button onClick={handleBackAbout} variant="outline">
                  <LayoutDashboard className="w-4 h-4 mr-2" />
                  {t('backAbout')}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
