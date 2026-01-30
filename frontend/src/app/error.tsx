'use client';

import { Button } from '@/components/ui/Button';
import { Home, RefreshCw, ServerCrash } from 'lucide-react';
import { useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import * as Sentry from '@sentry/nextjs';

/**
 * Props for the global error boundary.
 */
interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/**
 * Renders a user-friendly error page with retry and home actions.
 */
export default function Error({ error, reset }: ErrorPageProps) {
  const tCommon = useTranslations('Common');
  const tErrorPage = useTranslations('ErrorPage');

  useEffect(() => {
    console.error(error);
    Sentry.captureException(error);
  }, [error]);

  /**
   * Retries rendering by invoking the reset callback.
   */
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
            <h1 className="text-2xl font-bold text-bw-70">{tErrorPage('title')}</h1>
          </div>

          <p className="text-bw-70 text-sm leading-relaxed max-w-sm">{tErrorPage('description')}</p>

          <div className="flex md:flex-row flex-col gap-3 w-full max-w-xs justify-center">
            <Button onClick={handleTryAgain}>
              <RefreshCw className="w-4 h-4 mr-2" />
              {tCommon('tryAgain')}
            </Button>
            <Button asChild variant="outline">
              <Link href="/dashboard">
                <Home className="w-4 h-4 mr-2" />
                {tCommon('backToHome')}
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
