import Link from 'next/link';
import { Plus } from 'lucide-react';
import { getTranslations } from 'next-intl/server';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { Button } from '@/components/ui/Button';
import { UserProfileService } from '@/services/UserProfileService';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import StatCard from '@/components/common/StatCard';
import { calculateAverageScore } from '@/lib/utils/scoreUtils';
import { api } from '@/services/ApiServer';
import ConversationScenarioSuggestion from './components/ConversationScenarioSuggestion';
import DashboardTable from './components/DashboardTable';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/dashboard', true);
}

export default async function DashboardPage() {
  const t = await getTranslations('Dashboard');
  const tCommon = await getTranslations('Common');
  const userProfilePromise = UserProfileService.getUserProfile(api);
  const userStatsPromise = UserProfileService.getUserStats(api);
  const PAGE_SIZE = 3;
  const conversationScenariosPromise = conversationScenarioService.getConversationScenarios(
    api,
    1,
    PAGE_SIZE
  );
  const [userProfile, userStats, conversationScenarios] = await Promise.all([
    userProfilePromise,
    userStatsPromise,
    conversationScenariosPromise,
  ]);
  const averageScore = calculateAverageScore(userStats.scoreSum, userStats.totalSessions);
  const isAdmin = userProfile.accountRole === 'admin';

  return (
    <div className="flex flex-col gap-16">
      <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0">
        <p className="text-2xl text-center md:text-left">
          <span className="font-normal">{t('header.greeting')}</span>
          <span>{userProfile.fullName}!</span>
        </p>
        <Link href="/new-conversation-scenario" className="w-full md:w-auto">
          <Button size="full" className="md:!size-default">
            <Plus />
            {t('header.cta')}
          </Button>
        </Link>
      </section>

      <ConversationScenarioSuggestion
        suggestion={userProfile.scenarioAdvice.mascotSpeech}
        scenario={userProfile.scenarioAdvice.scenario}
      />

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard value={userStats.totalSessions} label={tCommon('totalSessions')} />
        <StatCard
          value={`${userStats.trainingTime.toFixed(2)}h`}
          label={t('userStats.trainingTime')}
        />
        <StatCard value={`${userStats.currentStreakDays}d`} label={t('userStats.currentStreak')} />
        <StatCard value={`${averageScore}/20`} label={tCommon('avgScore')} />
        <StatCard
          value={
            isAdmin
              ? `-/${userStats.dailySessionLimit}`
              : `${userStats.numRemainingDailySessions}/${userStats.dailySessionLimit}`
          }
          label={t('userStats.remainingSessionsToday')}
        />
      </div>

      <section className="flex flex-col gap-6">
        <div>
          <h2 className="text-xl">{t('recentSessions.title')}</h2>
          <p className="text-base text-bw-40">{t('recentSessions.subtitle')}</p>
        </div>
        <DashboardTable
          scenarios={conversationScenarios.data.scenarios}
          totalScenarios={conversationScenarios.data.totalScenarios}
          limit={PAGE_SIZE}
        />
      </section>
    </div>
  );
}
