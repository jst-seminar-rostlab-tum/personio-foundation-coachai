import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/LayoutProps';
import HistoryHeader from '@/components/layout/HistoryHeader';
import HistoryStats from '@/components/common/HistoryStats';
import PreviousSessions from '@/components/common/PreviousSessions';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/history', true);
}

export default function HistoryPage() {
  return (
    <div className="max-w-5xl mx-auto">
      <HistoryHeader />
      <div className="mt-8">
        <HistoryStats />
      </div>
      <div className="mt-8">
        <PreviousSessions />
      </div>
    </div>
  );
}
