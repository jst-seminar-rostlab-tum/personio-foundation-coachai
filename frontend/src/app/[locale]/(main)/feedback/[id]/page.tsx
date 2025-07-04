import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import FeedbackDetail from './components/FeedbackDetail';

interface FeedbackPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/feedback/[id]', true);
}

export default async function FeedbackDetailPage({ params }: FeedbackPageProps) {
  const { id } = await params;
  return <FeedbackDetail sessionId={id} />;
}
