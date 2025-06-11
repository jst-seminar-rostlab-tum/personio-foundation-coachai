import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import FeedbackDetail from './components/FeedbackDetail';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/feedback/[id]', true);
}

export default function FeedbackDetailPage() {
  return <FeedbackDetail />;
}
