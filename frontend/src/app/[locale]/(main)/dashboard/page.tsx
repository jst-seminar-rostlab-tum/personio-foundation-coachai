import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { ArrowRightIcon, Play, Plus } from 'lucide-react';

import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { Button } from '@/components/ui/Button';
import HistoryItem from '@/components/common/HistoryItem';
import DashboardStats from './components/DashboardStats';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/dashboard', true);
}

export default function DashboardPage() {
  const name = 'Anton';
  const t = useTranslations('Dashboard');

  return (
    <div className="flex flex-col gap-12 p-8">
      <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0">
        <p className="text-2xl text-center md:text-left">
          {t('header.greeting')}
          {name}!
        </p>
        <Link href="/new-training" className="w-full md:w-auto">
          <Button size="full" className="md:!size-default">
            <Plus />
            {t('header.cta')}
          </Button>
        </Link>
      </section>

      <section className="flex flex-col gap-4">
        <div>
          <h2 className="text-xl">{t('currentSession.title')}</h2>
          <p className="text-base text-bw-40">{t('currentSession.subtitle')}</p>
        </div>

        <div className="bg-marigold-5 border border-marigold-30 rounded-lg p-8 gap-8 flex flex-col">
          <div>
            <h2 className="text-xl">{t('currentSession.sessionCard.title')}</h2>
            <p className="text-base text-bw-40">{t('currentSession.sessionCard.subtitle')}</p>
          </div>
          <Link href="/simulation/1">
            <Button size="full" className="mx-auto">
              <Play />
              {t('currentSession.sessionCard.cta')}
            </Button>
          </Link>
        </div>
      </section>

      <DashboardStats />

      <section className="flex flex-col gap-4">
        <div>
          <h2 className="text-xl">{t('recentSessions.title')}</h2>
          <p className="text-base text-bw-40">{t('recentSessions.subtitle')}</p>
        </div>

        <HistoryItem
          title="Negotiating Job Offers"
          description="Practice salary negotiation with a potential candidate"
          date={new Date('2025-01-04T13:36:00')}
          duration={5672}
        />
        <HistoryItem
          title="Conflict Resolution"
          description="Mediate a disagreement between team members"
          date={new Date('2024-04-16T13:36:00')}
          duration={368}
        />
        <HistoryItem
          title="Performance Review"
          description="Conduct a quaterly performance review"
          date={new Date('2023-07-28T13:36:00')}
          duration={634}
        />

        <Link href="/history">
          <Button size="full">
            {t('recentSessions.cta')}
            <ArrowRightIcon />
          </Button>
        </Link>
      </section>
    </div>
  );
}
