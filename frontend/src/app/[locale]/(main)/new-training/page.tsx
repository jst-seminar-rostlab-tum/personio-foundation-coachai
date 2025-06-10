import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { Suspense } from 'react';
import { getConversationCategories } from '@/services/ConversationCategoriesService';
import NewTrainingForm from './components/NewTrainingForm';
import NewTrainingPageLoading from './loading';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/new-training', true);
}

export default function NewTrainingPage() {
  const categories = getConversationCategories();
  return (
    <Suspense fallback={<NewTrainingPageLoading />}>
      <NewTrainingForm categories={categories} />
    </Suspense>
  );
}
