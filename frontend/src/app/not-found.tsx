import { getTranslations } from 'next-intl/server';
import { Button } from '@/components/ui/Button';
import { TriangleAlert, Home } from 'lucide-react';
import Link from 'next/link';

export default async function NotFound() {
  const t = await getTranslations('NotFound');
  const tCommon = await getTranslations('Common');

  return (
    <div className="min-h-screen min-w-screen flex items-center justify-center py-4 px-4">
      <div className="w-full max-w-md text-center">
        <div className="flex flex-col items-center gap-6">
          <div className="w-16 h-16 bg-bw-10 rounded-full flex items-center justify-center">
            <TriangleAlert className="w-8 h-8 text-bw-40" />
          </div>

          <div className="space-y-2">
            <h1 className="text-2xl font-bold text-bw-70">{t('title')}</h1>
          </div>

          <p className="text-bw-40 text-sm leading-relaxed max-w-sm">{t('description')}</p>

          <div className="flex md:flex-row flex-col gap-3 w-full max-w-xs justify-center">
            <Button asChild>
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
