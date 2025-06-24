import { Suspense } from 'react';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { sessionService } from '@/services/server/SessionService';
import { UserProfileService } from '@/services/server/UserProfileService';
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
  const sessions = await sessionService.getPaginatedSessions(1, PAGE_SIZE);
  const userStatsData = UserProfileService.getUserStats();

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
