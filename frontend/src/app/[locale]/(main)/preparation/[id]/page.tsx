import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { ArrowLeftIcon, Play } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { useTranslations } from 'next-intl';
import { MetadataProps } from '@/interfaces/MetadataProps';
import PreparationContent from '../components/PreparationContent';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/preparation', true);
}

export default function PreparationPage() {
  const t = useTranslations('Preparation');

  return (
    <div className="flex flex-col gap-8 p-8">
      <h1 className="text-2xl text-center">{t('title')}</h1>

      <section className="flex flex-col gap-4 bg-marigold-5 border border-marigold-30 rounded-lg p-8 text-marigold-95">
        <h2 className="text-xl">{t('context.title')}</h2>
        <div className="text-base italic leading-loose">{t('context.description')}</div>
      </section>

      <PreparationContent />

      <div className="flex gap-4">
        <Link href="/new-training" className="flex-1">
          <Button size="full" variant="outline">
            <ArrowLeftIcon />
            {t('navigation.back')}
          </Button>
        </Link>

        <Link href="/simulation/1" className="flex-1">
          <Button size="full">
            <Play />
            {t('navigation.start')}
          </Button>
        </Link>
      </div>
    </div>
  );
}
