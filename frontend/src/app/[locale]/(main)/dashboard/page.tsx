import Link from 'next/link';
import { ArrowRightIcon, Plus } from 'lucide-react';
import { getLocale, getTranslations } from 'next-intl/server';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { Button } from '@/components/ui/Button';
import { sessionService } from '@/services/SessionService';
import { UserProfileService } from '@/services/UserProfileService';
import StatCard from '@/components/common/StatCard';
import EmptyListComponent from '@/components/common/EmptyListComponent';
import { SessionFromPagination } from '@/interfaces/models/Session';
import { formatDateFlexible } from '@/lib/utils/formatDateAndTime';
import { calculateAverageScore } from '@/lib/utils/scoreUtils';
import { api } from '@/services/ApiServer';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/dashboard', true);
}

export default async function DashboardPage() {
  const t = await getTranslations('Dashboard');
  const tCommon = await getTranslations('Common');
  const PAGE_SIZE = 3;
  const userProfilePromise = UserProfileService.getUserProfile(api);
  const userStatsPromise = UserProfileService.getUserStats(api);
  const sessionsPromise = sessionService.getPaginatedSessions(api, 1, PAGE_SIZE);
  const [userProfile, userStats, sessionsData] = await Promise.all([
    userProfilePromise,
    userStatsPromise,
    sessionsPromise,
  ]);
  const { sessions } = sessionsData.data;
  const locale = await getLocale();
  const isAdmin = userProfile.accountRole === 'admin';
  const averageScore = calculateAverageScore(userStats.scoreSum, userStats.totalSessions);
  
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
        <StatCard value={userStats.totalSessions} label={tCommon('totalSessions')} />
        <StatCard
          value={`${userStats.trainingTime.toFixed(1)}h`}
          label={t('userStats.trainingTime')}
        />
        <StatCard value={`${userStats.currentStreakDays}d`} label={t('userStats.currentStreak')} />
        <StatCard value={`${averageScore}/5`} label={tCommon('avgScore')} />
        <StatCard
          value={
            isAdmin
              ? `#/${userStats.dailySessionLimit}`
              : `${userStats.numRemainingDailySessions}/${userStats.dailySessionLimit}`
          }
          label={t('userStats.remainingSessionsToday')}
        />
      </div>

      <section className="flex flex-col gap-4">
        <div>
          <h2 className="text-xl">{t('recentSessions.title')}</h2>
          <p className="text-base text-bw-40">{t('recentSessions.subtitle')}</p>
        </div>
        {!sessions || sessions.length === 0 ? (
          <EmptyListComponent itemType={tCommon('sessions')} />
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
                    {formatDateFlexible(session.date, locale)}
                  </p>
                </div>
              </Link>
            ))}
            <Link href="/history">
              <Button size="full">
                {t('recentSessions.showEntireHistory')}
                <ArrowRightIcon />
              </Button>
            </Link>
          </>
        )}
      </section>
    </div>
  );
}
