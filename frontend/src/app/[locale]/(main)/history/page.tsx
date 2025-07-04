import { Suspense } from 'react';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { sessionService } from '@/services/SessionService';
import { UserProfileService } from '@/services/UserProfileService';
import { api } from '@/services/ApiServer';
import HistoryHeader from './components/HistoryHeader';
import HistoryStats from './components/HistoryStats';
import PreviousSessions from './components/PreviousSessions';
import Loading from './loading';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/history', true);
}

export default async function HistoryPage() {
  const PAGE_SIZE = 3;
  const sessions = await sessionService.getPaginatedSessions(api, 1, PAGE_SIZE);
  const userStatsData = await UserProfileService.getUserStats(api);

  return (
    <Suspense fallback={<Loading />}>
      <div className="flex flex-col gap-12">
        <HistoryHeader />
        <HistoryStats stats={userStatsData} />
        <PreviousSessions {...sessions.data} />
      </div>
    </Suspense>
  );
}
