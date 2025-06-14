import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import BackButton from '@/components/common/BackButton';
import NewTrainingForm from './components/NewTrainingForm';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/new-training', true);
}

export default function NewTrainingPage() {
  return (
    <>
      <BackButton />
      <NewTrainingForm />
    </>
  );
}
