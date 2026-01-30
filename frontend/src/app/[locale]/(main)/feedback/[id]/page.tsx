import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { getTranslations } from 'next-intl/server';
import FeedbackDetail from './components/FeedbackDetail';

/**
 * Props for the feedback detail route.
 */
interface FeedbackPageProps {
  params: Promise<{ id: string }>;
}

/**
 * Generates localized metadata for feedback detail pages.
 */
export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/feedback/[id]', true);
}

/**
 * Renders the feedback detail page with AI disclaimer.
 */
export default async function FeedbackDetailPage({ params }: FeedbackPageProps) {
  const { id } = await params;
  const tCommon = await getTranslations('Common');

  return (
    <div>
      <FeedbackDetail sessionId={id} />
      <div className="mt-4 text-center">
        <p className="text-xs text-bw-50">{tCommon('aiDisclaimer')}</p>
      </div>
    </div>
  );
}
