import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { getSessionFeedback } from '@/services/SessionService';
import { FeedbackPageProps } from '@/interfaces/FeedbackQuoteProps';
import { Suspense } from 'react';
import FeedbackDetail from './components/FeedbackDetail';
import FeedbackDetailLoadingPage from './loading';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/feedback/[id]', true);
}

export default async function FeedbackDetailPage({ params }: FeedbackPageProps) {
  const { id } = await params;
  const sessionFeedback = getSessionFeedback(id);

  return (
    <Suspense fallback={FeedbackDetailLoadingPage()}>
      <FeedbackDetail sessionFeedbackData={sessionFeedback} />
    </Suspense>
  );
}
