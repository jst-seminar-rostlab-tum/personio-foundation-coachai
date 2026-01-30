import { Button } from '@/components/ui/Button';
import { RotateCcw } from 'lucide-react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';

/**
 * Props for the history header.
 */
interface HistoryHeaderProps {
  scenarioId: string;
}

/**
 * Renders the history header and restart scenario button.
 */
export default function HistoryHeader({ scenarioId }: HistoryHeaderProps) {
  const t = useTranslations('Common');
  const tPersonalization = useTranslations('PersonalizationOptions');
  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0 mb-6">
        <div className="flex flex-col items-center md:items-start text-center md:text-left">
          <div className="text-2xl font-bold text-bw-70">{tPersonalization('myScenario')}</div>
        </div>
        <Link href={`/preparation/${scenarioId}`}>
          <Button className="w-full md:w-auto md:!size-default">
            <RotateCcw />
            {t('tryAgain')}
          </Button>
        </Link>
      </section>
    </div>
  );
}
