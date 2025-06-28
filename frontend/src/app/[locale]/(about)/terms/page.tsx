import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { useTranslations } from 'next-intl';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/terms', false);
}

export default function TermsOfServicePage() {
  const t = useTranslations('TermsOfService');

  return (
    <div className="flex flex-col justify-between min-h-screen">
      <section className="flex flex-col gap-8">
        <h1 className="text-4xl font-semibold break-words">{t('title')}</h1>
        <h2 className="text-xl font-semibold">{t('sections.limitationOfLiability.title')}</h2>
        <p className="text-base leading-loose">{t('sections.limitationOfLiability.content')}</p>
      </section>
    </div>
  );
}
