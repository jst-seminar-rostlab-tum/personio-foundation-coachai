import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { useTranslations } from 'next-intl';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/privacy', false);
}

export default function PrivacyPolicyPage() {
  const t = useTranslations('PrivacyPolicy');

  return (
    <div className="flex flex-col justify-between min-h-screen">
      <section className="flex flex-col gap-8">
        <h1 className="text-4xl font-semibold break-words">{t('title')}</h1>
        <h2 className="text-xl font-semibold">{t('sections.dataCollection.title')}</h2>
        <p className="text-base leading-loose">{t('sections.dataCollection.content')}</p>
      </section>
    </div>
  );
}
