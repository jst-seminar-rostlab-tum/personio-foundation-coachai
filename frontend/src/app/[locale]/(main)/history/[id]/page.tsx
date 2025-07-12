import { Suspense } from 'react';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { UserProfileService } from '@/services/UserProfileService';
import { api } from '@/services/ApiServer';
import ScenarioBox from '@/components/ui/ScenarioBox';
import HistoryHeader from './components/HistoryHeader';
import Loading from './loading';
import HistoryTable from './components/HistoryTable';
import HistoryStats from './components/HistoryStats';
import { StatisticsLabel, PreviousSessionsLabel } from './components/HistoryLabels';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/history', true);
}

export default async function HistoryPage() {
  const difficulty: 'easy' | 'medium' | 'hard' = 'hard';
  const userStatsData = await UserProfileService.getUserStats(api);
  return (
    <Suspense fallback={<Loading />}>
      <div className="flex flex-col gap-12">
        <div className="flex flex-col gap-8">
          <HistoryHeader />
          <ScenarioBox
            header="Salary Discussions"
            description={`"Current Salary - The other party earns slightly below the midpoint for Program Officers in this NGO. - Last annual raise was 4%. Performance Context - Solid on creative outreach and community partnerships. - Mixed record on deadlines and internal coordination. Recent Request - Last week, the other party emailed HR asking for a 10% raise, citing cost of living and workload growth. Organizational Context - The NGO faces tight budgets due to a new funder’s spending cap. - Managers can approve up to 3% merit raise without director sign-off. Silver Lining Peers respect the other party’s community engagement; manager has praised initiative on outreach campaigns."`}
            difficulty={difficulty}
            personalizationItems={[
              {
                title: 'Personality',
                description: 'This is the first personalization setting description.',
              },
              {
                title: 'Behavioral Traits',
                description: 'This is the second personalization setting description.',
              },
              {
                title: 'Training Focus',
                description: 'This is the third personalization setting description.',
              },
            ]}
          />
        </div>
        <StatisticsLabel />
        <HistoryStats stats={userStatsData} />
        <div className="flex flex-col gap-6">
          <PreviousSessionsLabel />
          <div className="overflow-x-auto rounded-lg border border-bw-20 mb-4 max-w-full">
            <HistoryTable />
          </div>
        </div>
      </div>
    </Suspense>
  );
}
