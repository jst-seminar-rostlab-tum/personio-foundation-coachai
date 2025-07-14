import Link from 'next/link';
import { Plus } from 'lucide-react';
import { getTranslations } from 'next-intl/server';

import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { Button } from '@/components/ui/Button';
import { UserProfileService } from '@/services/UserProfileService';
import StatCard from '@/components/common/StatCard';
import { calculateAverageScore } from '@/lib/utils/scoreUtils';
import { api } from '@/services/ApiServer';
import ClickableTable from './components/DashboardTable';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/dashboard', true);
}

export default async function DashboardPage() {
  const t = await getTranslations('Dashboard');
  const tCommon = await getTranslations('Common');
  const userProfilePromise = UserProfileService.getUserProfile(api);
  const userStatsPromise = UserProfileService.getUserStats(api);
  const [userProfile, userStats] = await Promise.all([userProfilePromise, userStatsPromise]);
  const averageScore = calculateAverageScore(userStats.scoreSum, userStats.totalSessions);

  return (
    <div className="flex flex-col gap-16">
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
          value={`${userStats.trainingTime.toFixed(2)}h`}
          label={t('userStats.trainingTime')}
        />
        <StatCard value={`${userStats.currentStreakDays}d`} label={t('userStats.currentStreak')} />
        <StatCard value={`${averageScore}/5`} label={tCommon('avgScore')} />
      </div>

      <section className="flex flex-col gap-6">
        <div>
          <h2 className="text-xl">{t('recentSessions.title')}</h2>
          <p className="text-base text-bw-40">{t('recentSessions.subtitle')}</p>
        </div>
        <ClickableTable />
      </section>
    </div>
  );
}
