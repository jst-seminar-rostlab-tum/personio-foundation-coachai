import { useTranslations } from 'next-intl';
import { Suspense } from 'react';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { UserProfileService } from '@/services/UserProfileService';
import { api } from '@/services/ApiServer';
import { Badge } from '@/components/ui/Badge';
import HistoryHeader from './components/HistoryHeader';
import Loading from './loading';
import HistoryTable from './HistoryTable';
import HistoryStats from './components/HistoryStats';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/history', true);
}

function ClientPreviousSessionsLabel() {
  const t = useTranslations('History');
  return <div className="text-xl font-bold text-bw-70">{t('previousSessions')}</div>;
}

function ClientStatisticsTitle() {
  const t = useTranslations('History');
  return <div className="text-xl font-bold text-bw-70">{t('statistics')}</div>;
}

function DifficultyLabel() {
  const t = useTranslations('History');
  return <div className="text-lg not-italic text-bw-70">{t('difficulty')}</div>;
}

export default async function HistoryPage() {
  const difficulty: 'easy' | 'medium' | 'hard' = 'hard';
  const userStatsData = await UserProfileService.getUserStats(api);
  return (
    <Suspense fallback={<Loading />}>
      <div className="flex flex-col gap-12">
        <div className="flex flex-col gap-8">
          <HistoryHeader />
          <div className="flex flex-col gap-12 w-full leading-loose border border-bw-20 rounded-lg p-8 text-bw-70 text-base mb-2">
            <span className="italic">
              &quot;Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
              incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
              exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure
              dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
              pariatur.&quot;
            </span>
            <div className="flex flex-col gap-2">
              <DifficultyLabel />
              <Badge difficulty={difficulty}>
                {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
              </Badge>
            </div>
          </div>
        </div>
        <ClientStatisticsTitle />
        <HistoryStats stats={userStatsData} />
        <div className="flex flex-col gap-6">
          <ClientPreviousSessionsLabel />
          <div className="overflow-x-auto rounded-lg border border-bw-20 mb-4 max-w-full">
            <HistoryTable />
          </div>
        </div>
      </div>
    </Suspense>
  );
}
