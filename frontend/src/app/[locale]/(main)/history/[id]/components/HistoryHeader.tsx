import { Button } from '@/components/ui/Button';
import { RotateCcw } from 'lucide-react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';

export default function HistoryHeader() {
  const t = useTranslations('History');
  return (
    <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0 mb-6">
      <div className="flex flex-col items-center md:items-start text-center md:text-left">
        <div className="text-2xl font-bold text-bw-70">Context</div>
      </div>
      <Link href="/preparation/1" passHref legacyBehavior>
        <Button className="w-full md:w-auto md:!size-default">
          <RotateCcw />
          {t('practiceAgain')}
        </Button>
      </Link>
    </section>
  );
}
