import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import BackButton from '@/components/common/BackButton';
import HistoryHeader from './components/HistoryHeader';
import HistoryStats from './components/HistoryStats';
import PreviousSessions from './components/PreviousSessions';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/history', true);
}

export default function HistoryPage() {
  return (
    <>
      <BackButton />
      <div className="flex flex-col gap-12">
        <HistoryHeader />
        <HistoryStats />
        <PreviousSessions />
      </div>
    </>
  );
}
