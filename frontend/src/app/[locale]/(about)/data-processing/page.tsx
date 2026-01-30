import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { getTranslations } from 'next-intl/server';
import PrivacyDialog from '@/app/[locale]/(auth)/login/components/PrivacyDialog';
import React from 'react';

/**
 * Generates localized metadata for the data processing policy page.
 */
export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/data-processing', false);
}

/**
 * Shows the data processing policy content via the shared privacy dialog.
 */
export default async function DataProcessingPage() {
  const tCommon = await getTranslations('Common');
  return (
    <div className="flex flex-col justify-between min-h-screen">
      <section className="flex flex-col gap-8">
        <h1 className="text-4xl font-semibold break-words">{tCommon('dataProcessingPolicy')}</h1>
        <PrivacyDialog variant="content" />
      </section>
    </div>
  );
}
