import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import TrainingSettings from '@/components/common/TrainingSettings';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/training-settings', true);
}

export default function TrainingSettingsPage() {
  return <TrainingSettings />;
}
