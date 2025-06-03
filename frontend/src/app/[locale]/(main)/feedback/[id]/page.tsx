import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/LayoutProps';
import { FeedbackPageProps } from '@/interfaces/Feedback';
import FeedbackDetail from './FeedbackDetail';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/feedback/[id]', true);
}

export default async function FeedbackDetailPage({ params }: FeedbackPageProps) {
  const { id } = await params;
  return <FeedbackDetail id={id} />;
}
