import Link from 'next/link';
import { useTranslations } from 'next-intl';

import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';

import type { Props } from '@/interfaces/LayoutProps';
import { Button } from '@/components/ui/Button';
import HistoryItem from '@/components/layout/HistoryItem';
import StatCard from '@/components/layout/StatCard';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/dashboard', true);
}

export default function DashboardPage() {
  const name = 'Anton';
  const t = useTranslations('Dashboard');

  return (
    <div className="flex flex-col gap-12 p-8">
      {/* Header */}
      <section className="flex items-center justify-between">
        <p className="text-2xl">
          {t('header.greeting')}
          {name}
        </p>
        <Link href="/new-training">
          <Button>{t('header.cta')}</Button>
        </Link>
      </section>

      {/* Current Session */}
      <section className="flex flex-col gap-4">
        <div>
          <h2 className="text-xl">{t('currentSession.title')}</h2>
          <p className="text-base text-[var(--bw-40)]">{t('currentSession.subtitle')}</p>
        </div>

        {/* Current Session Card */}
        <div className="bg-[var(--marigold-5)] border border-[var(--marigold-30)] rounded-lg p-8 gap-8 flex flex-col">
          <div>
            <h2 className="text-xl">{t('currentSession.sessionCard.title')}</h2>
            <p className="text-base text-[var(--bw-40)]">
              {t('currentSession.sessionCard.subtitle')}
            </p>
          </div>
          <Link href="/simulation/1">
            <Button className="w-full mx-auto">{t('currentSession.sessionCard.cta')}</Button>
          </Link>
        </div>
      </section>

      {/* Simple Stats: 2x2 on small, 1x4 on large screens */}
      {/* Stats Grid (2x2 on small, 1x4 on large screens) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard value={56} label={t('userStats.totalSessions')} />
        <StatCard value={12} label={t('userStats.monthlySessions')} />
        <StatCard value="4.8" label={t('userStats.avgRating')} />
        <StatCard value="89%" label={t('userStats.completionRate')} />
      </div>

      {/* Recent Training History */}
      <section className="flex flex-col gap-4">
        <div>
          <h2 className="text-xl">{t('recentSessions.title')}</h2>
          <p className="text-base text-[var(--bw-40)]">{t('recentSessions.subtitle')}</p>
        </div>

        {/* History Items */}
        <HistoryItem
          title="Negotiating Job Offers"
          description="Practice salary negotiation with a potential candidate"
          date={new Date('2025-01-04T13:36:00')}
          duration={5672} // 1h 34m 32s
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
          <Button className="w-full">{t('recentSessions.cta')}</Button>
        </Link>
      </section>
    </div>
  );
}
