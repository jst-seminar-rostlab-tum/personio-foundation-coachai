'use client';

import { ArrowLeftIcon } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils/cnMerge';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useTranslations } from 'next-intl';

export default function BackButton() {
  const t = useTranslations('Common');
  const pathname = usePathname();

  if (pathname.includes('/dashboard') || pathname.includes('/preparation')) {
    return null;
  }
  return (
    <Link href="/dashboard" className="block w-fit">
      <Button
        variant="ghost"
        className={cn(
          'group relative flex items-center gap-2 bg-transparent mb-8 p-0 text-xl text-bw-40 transition-colors duration-200 hover:text-bw-70 hover:bg-transparent'
        )}
      >
        <ArrowLeftIcon className="h-4 w-4" strokeWidth={3} />
        <span className="relative transition-transform duration-200 group-hover:-translate-x-1">
          {t('backToHome')}
        </span>
      </Button>
    </Link>
  );
}
