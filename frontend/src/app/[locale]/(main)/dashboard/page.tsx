import Link from 'next/link';
import { ArrowRightIcon, Plus } from 'lucide-react';
import { getLocale, getTranslations } from 'next-intl/server';

import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { Button } from '@/components/ui/Button';
import { sessionService } from '@/services/server/SessionService';
import { api } from '@/services/server/Api';
import { UserProfileService } from '@/services/server/UserProfileService';
import StatCard from '@/components/common/StatCard';
import EmptyListComponent from '@/components/common/EmptyListComponent';
import { SessionFromPagination } from '@/interfaces/models/Session';
import { formattedDate } from '@/lib/utils';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/dashboard', true);
}

export default async function DashboardPage() {
  const t = await getTranslations('Dashboard');
  const tCommon = await getTranslations('Common');
  const PAGE_SIZE = 3;
  const userProfile = await UserProfileService.getUserProfile();
  const userStatsData = await UserProfileService.getUserStats();
  const sessionsData = await sessionService.getPaginatedSessions(api, 1, PAGE_SIZE);
  const sessions = sessionsData?.data?.sessions;
  const locale = await getLocale();

  return (
    <div className="flex flex-col gap-12">
      <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0">
        <p className="text-2xl text-center md:text-left">
          {t('header.greeting')}
          {userProfile.fullName}!
        </p>
        <Link href="/new-conversation-scenario" className="w-full md:w-auto">
          <Button size="full" className="md:!size-default">
            <Plus />
            {t('header.cta')}
          </Button>
        </Link>
      </section>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard value={userStatsData.totalSessions} label={t('userStats.totalSessions')} />
        <StatCard
          value={`${userStatsData.trainingTime.toFixed(1)}h`}
          label={t('userStats.trainingTime')}
        />
        <StatCard
          value={`${userStatsData.currentStreakDays}d`}
          label={t('userStats.currentStreak')}
        />
        <StatCard value={`${userStatsData.averageScore}%`} label={t('userStats.avgScore')} />
      </div>

      <section className="flex flex-col gap-4">
        <div>
          <h2 className="text-xl">{t('recentSessions.title')}</h2>
          <p className="text-base text-bw-40">{t('recentSessions.subtitle')}</p>
        </div>
        {!sessions || sessions.length === 0 ? (
          <EmptyListComponent itemType={tCommon('emptyList.sessions')} />
        ) : (
          <>
            {sessions.map((session: SessionFromPagination) => (
              <Link
                key={session.sessionId}
                href={`/feedback/${session.sessionId}`}
                className="border border-bw-20 rounded-lg p-8 flex justify-between items-center gap-x-8 cursor-pointer transition-all duration-300 hover:shadow-md"
              >
                <div className="flex flex-col gap-2">
                  <h2 className="text-xl">{session.title}</h2>
                  <p className="text-base text-bw-40">{session.summary}</p>
                </div>
                <div className="flex flex-col justify-center text-center min-w-max">
                  <p className="text-base whitespace-nowrap">
                    {formattedDate(session.date, locale)}
                  </p>
                </div>
              </Link>
            ))}
            <Link href="/history">
              <Button size="full">
                {t('recentSessions.cta')}
                <ArrowRightIcon />
              </Button>
            </Link>
          </>
        )}
      </section>
    </div>
  );
}
