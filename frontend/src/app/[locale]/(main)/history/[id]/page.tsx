import { useTranslations } from 'next-intl';
import { Suspense } from 'react';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import HistoryHeader from './components/HistoryHeader';
import Loading from './loading';
import HistoryTable from './HistoryTable';

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
  return <div className="text-xl font-medium not-italic text-bw-70 mb-2">{t('difficulty')}</div>;
}

export default async function HistoryPage() {
  return (
    <Suspense fallback={<Loading />}>
      <div className="flex flex-col gap-12">
        <div className="flex flex-col gap-8">
          <HistoryHeader />
          <div className="flex flex-col gap-12 w-full leading-loose border border-bw-20 rounded-lg p-8 text-bw-70 text-base italic mb-2">
            &quot;Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
            incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
            exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure
            dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
            pariatur.&quot;
            <div className="flex flex-col gap-2">
              <DifficultyLabel />
              <div className="text-base not-italic text-bw-70">hard</div>
            </div>
          </div>
        </div>
        <ClientStatisticsTitle />
        <span>(Another PR)</span>
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
