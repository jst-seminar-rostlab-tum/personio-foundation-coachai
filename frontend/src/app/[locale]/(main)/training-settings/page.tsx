import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/LayoutProps';
import TrainingSettings from '../../../../components/common/TrainingSettings';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/training-settings', true);
}

export default function TrainingSettingsPage() {
  return <TrainingSettings />;
}
