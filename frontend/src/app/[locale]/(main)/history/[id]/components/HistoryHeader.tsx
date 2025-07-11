'use client';

import { Button } from '@/components/ui/Button';
import { ArrowRight } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';

export default function HistoryHeader() {
  const t = useTranslations('History');
  const router = useRouter();
  return (
    <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0 mb-6">
      <div className="flex flex-col items-center md:items-start text-center md:text-left">
        <div className="text-2xl font-bold text-bw-70">Context</div>
      </div>
      <Button
        className="w-full md:w-auto md:!size-default"
        type="button"
        onClick={() => router.push('/preparation/1')}
      >
        <ArrowRight />
        {t('practiceAgain')}
      </Button>
    </section>
  );
}
