import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { getTranslations } from 'next-intl/server';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/privacy', false);
}

export default async function PrivacyPolicyPage() {
  const t = await getTranslations('PrivacyPolicy');
  const tCommon = await getTranslations('Common');

  return (
    <div className="flex flex-col justify-between min-h-screen">
      <section className="flex flex-col gap-8">
        <h1 className="text-4xl font-semibold break-words">{tCommon('privacyPolicy')}</h1>
        <h2 className="text-xl font-semibold">{t('sections.dataCollection.title')}</h2>
        <p className="text-base leading-loose">{t('sections.dataCollection.content')}</p>
      </section>
    </div>
  );
}
