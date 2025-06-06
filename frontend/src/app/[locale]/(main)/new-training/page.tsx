import NewTrainingForm from '@/components/common/NewTrainingForm';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/new-training', true);
}

export default function NewTrainingPage() {
  return <NewTrainingForm />;
}
