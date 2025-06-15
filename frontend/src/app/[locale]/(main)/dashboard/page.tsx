import Link from 'next/link';
import { Play, Plus } from 'lucide-react';
import { getTranslations } from 'next-intl/server';

import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { Button } from '@/components/ui/Button';
import { api } from '@/services/ApiServer';
import { getPaginatedSessions } from '@/services/SessionService';
import StatCard from '@/components/common/StatCard';
import HistoryItems from './components/HistoryItems';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/dashboard', true);
}

export default async function DashboardPage() {
  const name = 'Anton';
  const t = await getTranslations('Dashboard');
  const PAGE_SIZE = 3;
  const sessions = getPaginatedSessions(api, 1, PAGE_SIZE);
  return (
    <div className="flex flex-col gap-12">
      <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0">
        <p className="text-2xl text-center md:text-left">
          {t('header.greeting')}
          {name}!
        </p>
        <Link href="/new-conversation-scenario" className="w-full md:w-auto">
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

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard value={56} label={t('userStats.totalSessions')} />
        <StatCard value="17.2h" label={t('userStats.trainingTime')} />
        <StatCard value="37d" label={t('userStats.currentStreak')} />
        <StatCard value="89%" label={t('userStats.avgScore')} />
      </div>

      <HistoryItems sessionsPromise={sessions} />
    </div>
  );
}
